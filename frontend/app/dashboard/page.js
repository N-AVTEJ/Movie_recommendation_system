"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import MovieCard from '../../components/MovieCard';
import MovieDetailsModal from '../../components/MovieDetailsModal';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:5000';

// Mood config — matches MOOD_GENRE_MAP in backend/recommendation.py
const MOODS = [
    { key: 'Happy', emoji: '😄', color: '#FFD700' },
    { key: 'Sad', emoji: '😢', color: '#6495ED' },
    { key: 'Romantic', emoji: '❤️', color: '#FF69B4' },
    { key: 'Action', emoji: '🔥', color: '#FF6B35' },
    { key: 'Motivational', emoji: '💪', color: '#32CD32' },
    { key: 'Neutral', emoji: '😐', color: '#888' },
    { key: 'Angry', emoji: '😠', color: '#FF4500' },
    { key: 'Fearful', emoji: '😨', color: '#9B59B6' },
    { key: 'Surprised', emoji: '😲', color: '#3498DB' },
];


export default function Dashboard() {
    const router = useRouter();
    const [user, setUser] = useState(null);

    // Core data
    const [movies, setMovies] = useState([]);
    const [watchlist, setWatchlist] = useState([]);
    const [userRatings, setUserRatings] = useState({});

    // UI state
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [activeTab, setActiveTab] = useState('home'); // home | mood | search | trending | profile | webcam | diversity

    // Search
    const [searchQuery, setSearchQuery] = useState('');
    const [nlQuery, setNlQuery] = useState('');
    const [nlResults, setNlResults] = useState([]);
    const [nlLoading, setNlLoading] = useState(false);

    // Filters (Home tab)
    const [selectedGenre, setSelectedGenre] = useState('');
    const [selectedLanguage, setSelectedLanguage] = useState('');
    const [sortBy, setSortBy] = useState('');

    // Mood
    const [activeMood, setActiveMood] = useState(null);
    const [moodRecommendations, setMoodRecommendations] = useState([]);
    const [recLoading, setRecLoading] = useState(false);

    // Trending
    const [trending, setTrending] = useState([]);
    const [trendingLoading, setTrendingLoading] = useState(false);
    const [trendingSource, setTrendingSource] = useState('');

    // Hybrid & Diverse recommendations
    const [hybridRecs, setHybridRecs] = useState([]);
    const [diverseRecs, setDiverseRecs] = useState([]);
    const [colabRecs, setColabRecs] = useState([]);

    // Taste Profile
    const [tasteProfile, setTasteProfile] = useState(null);
    const [profileLoading, setProfileLoading] = useState(false);

    // Weekend detection
    const [isWeekend, setIsWeekend] = useState(false);

    // ──────────────────────────────────────────────────────────
    // INIT
    // ──────────────────────────────────────────────────────────
    useEffect(() => {
        const day = new Date().getDay();
        setIsWeekend(day === 0 || day === 6);

        const userData = localStorage.getItem('user');
        if (!userData) { router.push('/login'); return; }
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);

        fetchMovies();
        fetchWatchlist(parsedUser.id);
        fetchUserRatings(parsedUser.id);
        fetchTrending();
        fetchColaborative(parsedUser.id);
        fetchDiverse();
    }, []);

    // ──────────────────────────────────────────────────────────
    // DATA FETCHERS
    // ──────────────────────────────────────────────────────────
    const fetchMovies = async () => {
        try {
            const res = await fetch(`${API_BASE}/movies`);
            const data = await res.json();
            setMovies(data.movies || []);
        } catch (err) { console.error(err); }
    };

    const fetchWatchlist = async (userId) => {
        try {
            const res = await fetch(`${API_BASE}/watchlist?user_id=${userId}`);
            const data = await res.json();
            setWatchlist(data.watchlist || []);
        } catch (err) { console.error(err); }
    };

    const fetchUserRatings = async (userId) => {
        try {
            const res = await fetch(`${API_BASE}/ratings/${userId}`);
            const data = await res.json();
            const ratingsMap = {};
            (data.ratings || []).forEach(r => { ratingsMap[r.movie_id] = r.rating; });
            setUserRatings(ratingsMap);
        } catch (err) { console.error(err); }
    };

    const fetchTrending = async () => {
        setTrendingLoading(true);
        try {
            const res = await fetch(`${API_BASE}/trending`);
            const data = await res.json();
            setTrending(data.trending || []);
            setTrendingSource(data.source || 'local');
        } catch (err) { console.error(err); }
        finally { setTrendingLoading(false); }
    };

    const fetchColaborative = async (userId) => {
        try {
            const res = await fetch(`${API_BASE}/recommend/collaborative`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, top_n: 8 })
            });
            const data = await res.json();
            setColabRecs(data.recommendations || []);
        } catch (err) { console.error(err); }
    };

    const fetchDiverse = async () => {
        try {
            const res = await fetch(`${API_BASE}/recommend/diverse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ top_n: 8 })
            });
            const data = await res.json();
            setDiverseRecs(data.recommendations || []);
        } catch (err) { console.error(err); }
    };

    const fetchTasteProfile = async () => {
        if (!user) return;
        setProfileLoading(true);
        try {
            const res = await fetch(`${API_BASE}/user/${user.id}/profile`);
            const data = await res.json();
            setTasteProfile(data);
        } catch (err) { console.error(err); }
        finally { setProfileLoading(false); }
    };

    // ──────────────────────────────────────────────────────────
    // MOOD ENGINE
    // ──────────────────────────────────────────────────────────
    const handleMoodSelect = async (mood) => {
        if (activeMood === mood) {
            setActiveMood(null); setMoodRecommendations([]); return;
        }
        setActiveMood(mood);
        setRecLoading(true);
        setMoodRecommendations([]);
        try {
            const res = await fetch(`${API_BASE}/mood`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mood, top_n: 8 })
            });
            const data = await res.json();
            setMoodRecommendations(data.recommendations || []);
        } catch (err) { console.error(err); }
        finally { setRecLoading(false); }
    };

    // ──────────────────────────────────────────────────────────
    // NATURAL LANGUAGE SEARCH
    // ──────────────────────────────────────────────────────────
    const handleNLSearch = async (e) => {
        e.preventDefault();
        if (!nlQuery.trim()) return;
        setNlLoading(true);
        setNlResults([]);
        try {
            const res = await fetch(`${API_BASE}/search/natural`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: nlQuery, top_n: 8 })
            });
            const data = await res.json();
            setNlResults(data.results || []);
        } catch (err) { console.error(err); }
        finally { setNlLoading(false); }
    };

    // ──────────────────────────────────────────────────────────
    // MOVIE INTERACTION
    // ──────────────────────────────────────────────────────────
    const handleMovieClick = useCallback(async (movie) => {
        console.log("Selection Trace - Clicked Movie:", movie);
        if (!movie || !movie.id) {
            console.error("Selection Trace - Invalid movie object:", movie);
            return;
        }

        // Enrich with trailer if available
        let enriched = { ...movie };
        try {
            console.log(`Selection Trace - Fetching trailer for ID: ${movie.id}`);
            const res = await fetch(`${API_BASE}/movie/${movie.id}/trailer`);
            if (res.ok) {
                const data = await res.json();
                enriched.trailer_embed = data.trailer_embed;
            }
        } catch (err) {
            console.warn("Selection Trace - Trailer fetch failed", err);
        }

        // If no reason, get hybrid recommendations for this movie
        if (!enriched.reason && user) {
            try {
                console.log(`Selection Trace - Fetching hybrid recs for ID: ${movie.id}`);
                const res = await fetch(`${API_BASE}/recommend/hybrid`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ movie_id: movie.id, user_id: user.id, top_n: 5 })
                });
                const data = await res.json();
                if (data.recommendations && data.recommendations.length > 0) {
                    setHybridRecs(data.recommendations);
                    enriched.hybridRecs = data.recommendations;
                }
            } catch (err) {
                console.warn("Selection Trace - Hybrid recs fetch failed", err);
            }
        }

        console.log("Selection Trace - Final enriched movie:", enriched.title);
        setSelectedMovie(enriched);
    }, [user, API_BASE]);

    const toggleWatchlist = async (movieId) => {
        if (!user) return;
        try {
            await fetch(`${API_BASE}/watchlist`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, movie_id: movieId })
            });
            fetchWatchlist(user.id);
        } catch (err) { console.error(err); }
    };

    const submitRating = async (movieId, rating) => {
        if (!user) return;
        try {
            await fetch(`${API_BASE}/rate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, movie_id: movieId, rating })
            });
            fetchUserRatings(user.id);
            // Re-fetch collaborative after rating
            fetchColaborative(user.id);
            alert('⭐ Rating saved! Recommendations updated.');
        } catch (err) { console.error(err); }
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        router.push('/');
    };

    // ──────────────────────────────────────────────────────────
    // FILTERING (Home tab)
    // ──────────────────────────────────────────────────────────
    let displayedMovies = movies.filter(movie => {
        const matchesSearch = movie.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (movie.genre && movie.genre.toLowerCase().includes(searchQuery.toLowerCase()));
        const matchesGenre = selectedGenre ? movie.genre?.includes(selectedGenre) : true;
        const matchesLanguage = selectedLanguage ? movie.language?.includes(selectedLanguage) : true;
        return matchesSearch && matchesGenre && matchesLanguage;
    });

    if (sortBy === 'rating') displayedMovies.sort((a, b) => b.rating - a.rating);
    else if (sortBy === 'title') displayedMovies.sort((a, b) => a.title.localeCompare(b.title));
    else if (sortBy === 'year') displayedMovies.sort((a, b) => b.release_year - a.release_year);

    const allGenres = [...new Set(movies.flatMap(m => (m.genre || '').split(', ')))].filter(Boolean);
    const allLanguages = [...new Set(movies.flatMap(m => (m.language || '').split(', ')))].filter(Boolean);

    const personalizedMovies = movies.filter(m => {
        if (!user?.preferences) return false;
        const prefs = user.preferences.toLowerCase().split(',').map(s => s.trim());
        return prefs.some(p => m.genre?.toLowerCase().includes(p) || m.mood?.toLowerCase().includes(p));
    }).slice(0, 6);

    if (!user) return null;

    // ──────────────────────────────────────────────────────────
    // RENDER
    // ──────────────────────────────────────────────────────────
    if (!user) {
        return (
            <div className="loading-screen" style={{
                height: '100vh', display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center', background: '#050505', color: '#fff'
            }}>
                <div className="loader" style={{
                    width: '40px', height: '40px', border: '3px solid rgba(255,255,255,0.1)',
                    borderTopColor: '#E50914', borderRadius: '50%', animation: 'spin 1s linear infinite'
                }}></div>
                <p style={{ marginTop: '1rem', letterSpacing: '1px', opacity: 0.8 }}>PREPARING CINEINDIA...</p>
                <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
        );
    }

    return (
        <div className="dashboard-wrapper">
            {/* ── SIDEBAR ── */}
            <aside className="sidebar">
                <div className="sidebar-logo">🎬 CineIndia</div>
                <nav className="sidebar-nav">
                    {[
                        { key: 'home', icon: '🏠', label: 'Home' },
                        { key: 'mood', icon: '🎭', label: 'Mood Engine' },
                        { key: 'search', icon: '🔍', label: 'AI Search' },
                        { key: 'trending', icon: '🔥', label: 'Trending' },
                        { key: 'diversity', icon: '🎯', label: 'Discover' },
                        { key: 'profile', icon: '📊', label: 'My Profile' },
                    ].map(tab => (
                        <button
                            key={tab.key}
                            className={`sidebar-btn ${activeTab === tab.key ? 'active' : ''}`}
                            onClick={() => {
                                setActiveTab(tab.key);
                                if (tab.key === 'profile') fetchTasteProfile();
                            }}
                        >
                            <span className="sidebar-icon">{tab.icon}</span>
                            <span className="sidebar-label">{tab.label}</span>
                        </button>
                    ))}
                </nav>
                <div className="sidebar-user">
                    <div className="sidebar-avatar">{user.username[0].toUpperCase()}</div>
                    <div>
                        <div className="sidebar-username">{user.username}</div>
                        <button className="sidebar-logout" onClick={handleLogout}>Logout</button>
                    </div>
                </div>
            </aside>

            {/* ── MAIN CONTENT ── */}
            <main className="main-content">

                {/* ═══════════════ HOME TAB ═══════════════ */}
                {activeTab === 'home' && (
                    <div>
                        {/* Welcome Banner */}
                        <div className="welcome-banner">
                            <div className="welcome-text">
                                <h1>Welcome back, <span className="gradient-text">{user?.username}</span> 👋</h1>
                                <p>
                                    {isWeekend
                                        ? "🎉 It's the weekend! Perfect for binge-watching that epic saga."
                                        : "📅 Weekday mode: Quick, gripping picks to fit your schedule."}
                                </p>
                            </div>
                            <div className="welcome-stats">
                                <div className="stat-pill">🎬 {movies.length} Movies</div>
                                <div className="stat-pill">👁️ {watchlist.length} Watchlist</div>
                                <div className="stat-pill">⭐ {Object.keys(userRatings).length} Rated</div>
                            </div>
                        </div>

                        {/* Cold Start Notice */}
                        {Object.keys(userRatings).length === 0 && user?.preferences && (
                            <div className="feature-banner cold-start">
                                <span className="feature-icon">❄️</span>
                                <div>
                                    <strong>Cold Start Solved!</strong>
                                    <p>Your quiz preferences <em>({user.preferences})</em> are powering your personalized feed below — no watch history needed.</p>
                                </div>
                            </div>
                        )}

                        {/* SVD Collaborative Section */}
                        {colabRecs.length > 0 && (
                            <section className="movie-section">
                                <div className="section-header">
                                    <h2>🤝 Recommended by AI (Collaborative Filtering)</h2>
                                    <span className="algo-badge">SVD Matrix Factorization</span>
                                </div>
                                <div className="movie-scroll">
                                    {colabRecs.map(movie => (
                                        <MovieCard key={`colab-${movie.id}`} movie={movie} onClick={handleMovieClick} />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Personalised by Preferences */}
                        {personalizedMovies.length > 0 && (
                            <section className="movie-section">
                                <div className="section-header">
                                    <h2>✨ Personalized for You</h2>
                                    <span className="algo-badge">TF-IDF Content Match</span>
                                </div>
                                <div className="movie-scroll">
                                    {personalizedMovies.map(movie => (
                                        <MovieCard key={`pref-${movie.id}`} movie={movie} onClick={handleMovieClick} />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Watchlist */}
                        {watchlist.length > 0 && (
                            <section className="movie-section">
                                <div className="section-header">
                                    <h2>📋 My Watchlist</h2>
                                    <span className="algo-badge">{watchlist.length} saved</span>
                                </div>
                                <div className="movie-scroll">
                                    {watchlist.map(movie => (
                                        <MovieCard key={`wl-${movie.id}`} movie={movie} onClick={handleMovieClick} />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Filters & Catalog */}
                        <div className="toolbar glassmorphism">
                            <input
                                type="text"
                                placeholder="🔎 Search movies, genres..."
                                className="search-input"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                            <select className="select-input" value={selectedLanguage} onChange={(e) => setSelectedLanguage(e.target.value)}>
                                <option value="">All Languages</option>
                                {allLanguages.map(l => <option key={l} value={l}>{l}</option>)}
                            </select>
                            <select className="select-input" value={selectedGenre} onChange={(e) => setSelectedGenre(e.target.value)}>
                                <option value="">All Genres</option>
                                {allGenres.map(g => <option key={g} value={g}>{g}</option>)}
                            </select>
                            <select className="select-input" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                                <option value="">Sort By</option>
                                <option value="rating">Rating ↓</option>
                                <option value="title">Title A-Z</option>
                                <option value="year">Newest First</option>
                            </select>
                        </div>

                        <section className="movie-section">
                            <div className="section-header">
                                <h2>🎬 Explore the Catalog</h2>
                                <span className="algo-badge">{displayedMovies.length} results</span>
                            </div>
                            <div className="movie-grid-full">
                                {displayedMovies.map(movie => (
                                    <MovieCard key={movie.id} movie={movie} onClick={handleMovieClick} />
                                ))}
                            </div>
                        </section>
                    </div>
                )}

                {/* ═══════════════ MOOD ENGINE TAB ═══════════════ */}
                {activeTab === 'mood' && (
                    <div>
                        <div className="tab-header">
                            <h1>🎭 Mood-Based Recommendation Engine</h1>
                            <p>Select your current mood — our system uses VADER sentiment analysis + genre mapping to find the perfect movies for how you feel right now.</p>
                        </div>

                        <div className="feature-banner">
                            <span className="feature-icon">🧠</span>
                            <div>
                                <strong>How it works:</strong>
                                <p>Each mood maps to specific genres (e.g. "Sad" → Drama/Romance). VADER sentiment analysis scores movie descriptions to find emotional alignment. Results are ranked by combined genre match + sentiment + rating.</p>
                            </div>
                        </div>

                        <div className="mood-grid">
                            {MOODS.map(mood => (
                                <button
                                    key={mood.key}
                                    className={`mood-card ${activeMood === mood.key ? 'active' : ''}`}
                                    style={{ '--mood-color': mood.color }}
                                    onClick={() => handleMoodSelect(mood.key)}
                                >
                                    <span className="mood-emoji">{mood.emoji}</span>
                                    <span className="mood-label">{mood.key}</span>
                                    {activeMood === mood.key && <span className="mood-active-dot"></span>}
                                </button>
                            ))}
                        </div>

                        {recLoading && (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Running VADER sentiment analysis + genre mapping...</p>
                            </div>
                        )}

                        {moodRecommendations.length > 0 && !recLoading && (
                            <div>
                                <div className="section-header" style={{ marginTop: '2rem' }}>
                                    <h2>Results for "{activeMood}" mood</h2>
                                    <span className="algo-badge">VADER + Genre Mapping</span>
                                </div>
                                <div className="movie-grid-full">
                                    {moodRecommendations.map(movie => (
                                        <MovieCard key={`mood-${movie.id}`} movie={movie} onClick={handleMovieClick} />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* ═══════════════ AI SEARCH TAB ═══════════════ */}
                {activeTab === 'search' && (
                    <div>
                        <div className="tab-header">
                            <h1>🔍 Natural Language AI Search</h1>
                            <p>Type naturally! Our NLP engine understands context, not just keywords.</p>
                        </div>

                        <div className="feature-banner">
                            <span className="feature-icon">🤖</span>
                            <div>
                                <strong>How it works (NLP Pipeline):</strong>
                                <p>Your query is vectorized using TF-IDF with bigrams on our movie corpus (title + genre + description + cast). VADER sentiment analysis aligns your query's emotional tone with movie descriptions for deeper semantic search.</p>
                            </div>
                        </div>

                        <form onSubmit={handleNLSearch} className="nl-search-form">
                            <input
                                type="text"
                                className="nl-search-input"
                                placeholder='Try: "mind-bending thriller like Inception" or "emotional drama about family"'
                                value={nlQuery}
                                onChange={(e) => setNlQuery(e.target.value)}
                            />
                            <button type="submit" className="ott-button" disabled={nlLoading}>
                                {nlLoading ? '🔍 Searching...' : '🚀 Search'}
                            </button>
                        </form>

                        <div className="search-suggestions">
                            <strong>Try these example queries:</strong>
                            {[
                                'I want a movie like Baahubali but more emotional',
                                'Action movie with a strong female lead',
                                'Something funny and light-hearted',
                                'Intense thriller with plot twists',
                            ].map(s => (
                                <button key={s} className="suggestion-chip" onClick={() => setNlQuery(s)}>
                                    {s}
                                </button>
                            ))}
                        </div>

                        {nlLoading && (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Running TF-IDF semantic search + sentiment alignment...</p>
                            </div>
                        )}

                        {nlResults.length > 0 && !nlLoading && (
                            <div>
                                <div className="section-header" style={{ marginTop: '2rem' }}>
                                    <h2>Search Results ({nlResults.length})</h2>
                                    <span className="algo-badge">TF-IDF + VADER Sentiment</span>
                                </div>
                                <div className="movie-grid-full">
                                    {nlResults.map(movie => (
                                        <MovieCard key={`nl-${movie.id}`} movie={movie} onClick={handleMovieClick} />
                                    ))}
                                </div>
                            </div>
                        )}

                        {nlResults.length === 0 && nlQuery && !nlLoading && (
                            <div className="empty-state">
                                <p>No results found. Try a different query!</p>
                            </div>
                        )}
                    </div>
                )}

                {/* ═══════════════ TRENDING TAB ═══════════════ */}
                {activeTab === 'trending' && (
                    <div>
                        <div className="tab-header">
                            <h1>🔥 Real-Time Trending Movies</h1>
                            <p>Live data from TMDB API — what the world is watching right now.</p>
                        </div>

                        {trendingSource === 'tmdb' && (
                            <div className="feature-banner tmdb-banner">
                                <span className="feature-icon">📡</span>
                                <div>
                                    <strong>Live TMDB Data</strong>
                                    <p>Fetching real-time trending movies from The Movie Database API. Blending global trends with your personalized taste profile.</p>
                                </div>
                            </div>
                        )}

                        {trendingSource === 'local_fallback' && (
                            <div className="feature-banner" style={{ borderColor: '#f39c12' }}>
                                <span className="feature-icon">📂</span>
                                <div>
                                    <strong>Local Catalog Top Picks</strong>
                                    <p>TMDB API unavailable — showing top-rated movies from our catalog. Add a valid TMDB API key to enable live trending data.</p>
                                </div>
                            </div>
                        )}

                        {trendingLoading ? (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Fetching live trending data from TMDB...</p>
                            </div>
                        ) : (
                            <div>
                                <div className="section-header">
                                    <h2>Trending This Week</h2>
                                    <button className="refresh-btn" onClick={fetchTrending}>🔄 Refresh</button>
                                </div>
                                <div className="movie-grid-full">
                                    {trending.map(movie => (
                                        <MovieCard key={`trend-${movie.id}`} movie={movie} onClick={handleMovieClick} />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* ═══════════════ DIVERSITY TAB ═══════════════ */}
                {activeTab === 'diversity' && (
                    <div>
                        <div className="tab-header">
                            <h1>🎯 Diversity-Aware Recommendations</h1>
                            <p>We fight filter bubbles using Maximal Marginal Relevance (MMR) — balancing relevance with intentional variety.</p>
                        </div>

                        <div className="feature-banner">
                            <span className="feature-icon">🎯</span>
                            <div>
                                <strong>Anti-Filter Bubble Algorithm (MMR):</strong>
                                <p>Standard recommenders trap you in a loop. Our MMR algorithm scores each pick by relevance minus similarity to already-selected items, ensuring you get both expected favorites AND surprising discoveries.</p>
                            </div>
                        </div>

                        <div className="algo-cards">
                            <div className="algo-card">
                                <div className="algo-icon">📐</div>
                                <div className="algo-name">Maximal Marginal Relevance</div>
                                <div className="algo-desc">λ=0.5 balances relevance vs. diversity</div>
                            </div>
                            <div className="algo-card">
                                <div className="algo-icon">🧮</div>
                                <div className="algo-name">TF-IDF Feature Vectors</div>
                                <div className="algo-desc">500-feature movie representation</div>
                            </div>
                            <div className="algo-card">
                                <div className="algo-icon">📊</div>
                                <div className="algo-name">Rating Normalization</div>
                                <div className="algo-desc">Combined score with genre diversity</div>
                            </div>
                        </div>

                        <section className="movie-section">
                            <div className="section-header">
                                <h2>Your Diverse Picks</h2>
                                <span className="algo-badge">MMR Diversity Algorithm</span>
                            </div>
                            <div className="movie-grid-full">
                                {diverseRecs.map(movie => (
                                    <MovieCard key={`div-${movie.id}`} movie={movie} onClick={handleMovieClick} />
                                ))}
                            </div>
                        </section>
                    </div>
                )}

                {/* ═══════════════ PROFILE / DASHBOARD TAB ═══════════════ */}
                {activeTab === 'profile' && (
                    <div>
                        <div className="tab-header">
                            <h1>📊 My Taste Profile Dashboard</h1>
                            <p>Visual analytics of your movie preferences, genre evolution, and rating patterns.</p>
                        </div>

                        {profileLoading ? (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Analyzing your taste profile...</p>
                            </div>
                        ) : tasteProfile ? (
                            tasteProfile.error ? (
                                <div className="feature-banner cold-start">
                                    <span className="feature-icon">❄️</span>
                                    <div>
                                        <strong>No rating history yet</strong>
                                        <p>Start rating movies to see your personalized taste evolution dashboard. Rate at least 3 movies to unlock insights.</p>
                                        <p style={{ marginTop: '0.5rem', color: '#aaa' }}>Current preferences from quiz: <em>{user.preferences || 'None set'}</em></p>
                                    </div>
                                </div>
                            ) : (
                                <div className="profile-dashboard">
                                    {/* Stats Row */}
                                    <div className="stats-row">
                                        <div className="stat-card">
                                            <div className="stat-number">{tasteProfile.total_ratings}</div>
                                            <div className="stat-label">Movies Rated</div>
                                        </div>
                                        <div className="stat-card">
                                            <div className="stat-number">{tasteProfile.avg_rating}</div>
                                            <div className="stat-label">Avg Rating</div>
                                        </div>
                                        <div className="stat-card">
                                            <div className="stat-number">{tasteProfile.max_rating}</div>
                                            <div className="stat-label">Highest Rated</div>
                                        </div>
                                        <div className="stat-card">
                                            <div className="stat-number">{Object.keys(tasteProfile.genre_distribution || {}).length}</div>
                                            <div className="stat-label">Genres Explored</div>
                                        </div>
                                    </div>

                                    <div className="charts-grid">
                                        {/* Genre Distribution */}
                                        <div className="chart-card glassmorphism">
                                            <h3>🎬 Genre Distribution</h3>
                                            <div className="bar-chart">
                                                {Object.entries(tasteProfile.genre_distribution || {}).map(([genre, count]) => {
                                                    const maxCount = Math.max(...Object.values(tasteProfile.genre_distribution));
                                                    const pct = (count / maxCount) * 100;
                                                    return (
                                                        <div key={genre} className="bar-row">
                                                            <div className="bar-label">{genre}</div>
                                                            <div className="bar-bg">
                                                                <div className="bar-fill" style={{ width: `${pct}%` }}></div>
                                                            </div>
                                                            <div className="bar-count">{count}</div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>

                                        {/* Mood Distribution */}
                                        <div className="chart-card glassmorphism">
                                            <h3>🎭 Mood Preferences</h3>
                                            <div className="donut-chart">
                                                {Object.entries(tasteProfile.mood_distribution || {}).map(([mood, count], i) => {
                                                    const colors = ['#E50914', '#00d2ff', '#FFD700', '#32CD32', '#FF69B4', '#FF6B35'];
                                                    return (
                                                        <div key={mood} className="mood-stat">
                                                            <div className="mood-dot" style={{ background: colors[i % colors.length] }}></div>
                                                            <span>{mood}</span>
                                                            <span className="mood-stat-count">{count}</span>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>

                                        {/* Top Cast */}
                                        {Object.keys(tasteProfile.top_cast || {}).length > 0 && (
                                            <div className="chart-card glassmorphism">
                                                <h3>⭐ Favorite Cast</h3>
                                                <div className="cast-list">
                                                    {Object.entries(tasteProfile.top_cast).map(([name, count]) => (
                                                        <div key={name} className="cast-item">
                                                            <div className="cast-avatar">{name[0]}</div>
                                                            <div>
                                                                <div className="cast-name">{name}</div>
                                                                <div className="cast-count">{count} movies watched</div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Top Rated Movies */}
                                        {tasteProfile.top_rated_movies?.length > 0 && (
                                            <div className="chart-card glassmorphism">
                                                <h3>🏆 Your Top Rated</h3>
                                                <div className="top-rated-list">
                                                    {tasteProfile.top_rated_movies.map((m, i) => (
                                                        <div key={i} className="top-rated-item">
                                                            <div className="top-rated-rank">#{i + 1}</div>
                                                            <div className="top-rated-title">{m.title}</div>
                                                            <div className="top-rated-score">⭐ {m.user_rating}/10</div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Taste Evolution */}
                                    {Object.keys(tasteProfile.year_preferences || {}).length > 0 && (
                                        <div className="chart-card glassmorphism" style={{ marginTop: '1.5rem' }}>
                                            <h3>📈 Taste Evolution by Release Year</h3>
                                            <div className="year-chart">
                                                {Object.entries(tasteProfile.year_preferences)
                                                    .sort(([a], [b]) => parseInt(a) - parseInt(b))
                                                    .map(([year, avg]) => (
                                                        <div key={year} className="year-bar">
                                                            <div className="year-fill-wrap">
                                                                <div
                                                                    className="year-fill"
                                                                    style={{ height: `${(avg / 10) * 80}%` }}
                                                                    title={`${year}: avg ${avg}/10`}
                                                                ></div>
                                                            </div>
                                                            <div className="year-label">{year}</div>
                                                            <div className="year-avg">{avg}</div>
                                                        </div>
                                                    ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )
                        ) : (
                            <div className="empty-state">
                                <p>Click "My Profile" to load your taste profile.</p>
                            </div>
                        )}
                    </div>
                )}
            </main>

            {/* ── MOVIE DETAILS MODAL ── */}
            <MovieDetailsModal
                movie={selectedMovie}
                onClose={() => setSelectedMovie(null)}
                inWatchlist={selectedMovie && watchlist.some(m => m.id === selectedMovie.id)}
                onToggleWatchlist={() => toggleWatchlist(selectedMovie.id)}
                onSubmitRating={submitRating}
                hybridRecs={hybridRecs}
                onMovieClick={handleMovieClick}
            />
        </div>
    );
}
