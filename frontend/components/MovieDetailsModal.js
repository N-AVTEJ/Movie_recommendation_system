import { useState, useEffect } from 'react';
import MovieCard from './MovieCard';

export default function MovieDetailsModal({ movie, onClose, inWatchlist, onToggleWatchlist, onSubmitRating, hybridRecs, onMovieClick }) {
    const [rating, setRating] = useState('');
    const [xaiLoading, setXaiLoading] = useState(true);
    const [showTrailer, setShowTrailer] = useState(false);
    const [activeSection, setActiveSection] = useState('details'); // details | trailer | similar

    useEffect(() => {
        if (movie) {
            console.log("Selection Trace - Modal received movie:", movie.title, movie.id);
            setXaiLoading(true);
            setShowTrailer(false);
            setActiveSection('details');
            setRating('');
            const timer = setTimeout(() => setXaiLoading(false), 900);
            return () => clearTimeout(timer);
        }
    }, [movie]);

    if (!movie) return null;

    const handleRating = () => {
        const r = parseFloat(rating);
        if (r >= 1 && r <= 10) {
            onSubmitRating(movie.id, r);
        } else {
            alert("Rating must be between 1 and 10");
        }
    };

    // Backdrop image for cinematic feel
    const backdropStyle = movie.poster_url ? {
        backgroundImage: `linear-gradient(to right, rgba(10,10,10,0.98) 40%, rgba(10,10,10,0.6) 80%), url(${movie.poster_url})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center right',
    } : {};

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" style={backdropStyle} onClick={(e) => e.stopPropagation()}>
                <button className="close-btn" onClick={onClose}>✕</button>

                <div className="modal-body">
                    {/* POSTER COLUMN */}
                    <div className="modal-poster">
                        <img
                            src={movie.poster_url}
                            alt={movie.title}
                            onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = 'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=350&h=500&auto=format&fit=crop';
                            }}
                        />
                    </div>

                    {/* DETAILS COLUMN */}
                    <div className="modal-details">
                        <h2>{movie.title} {movie.release_year ? <span style={{ color: '#888', fontWeight: 400, fontSize: '2rem' }}>({movie.release_year})</span> : ''}</h2>

                        <div className="tags">
                            {movie.genre && <span className="badge genre">{movie.genre}</span>}
                            {movie.language && <span className="badge language">{movie.language}</span>}
                            {movie.mood && <span className="badge mood">{movie.mood}</span>}
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '1.5rem' }}>
                            <p className="rating">⭐ {movie.rating}/10</p>
                            {movie.ott_platform && (
                                <button className="ott-button" style={{ padding: '0.4rem 1rem', fontSize: '0.85rem' }}>
                                    ▶ {movie.ott_platform}
                                </button>
                            )}
                        </div>

                        {movie.cast_members && (
                            <p className="cast" style={{ color: '#aaa', fontStyle: 'italic', marginBottom: '1rem', fontSize: '0.95rem' }}>
                                <strong style={{ color: '#ddd' }}>Cast:</strong> {movie.cast_members}
                            </p>
                        )}

                        <p className="description">{movie.description}</p>

                        {/* XAI Box */}
                        {xaiLoading ? (
                            <div className="recommendation-reason" style={{ opacity: 0.7 }}>
                                <strong>🧠 Analyzing Neural Match...</strong>
                                <p style={{ fontStyle: 'italic', opacity: 0.6 }}>Running TF-IDF + Cosine Similarity scoring against your taste profile...</p>
                            </div>
                        ) : (
                            <div className="recommendation-reason">
                                <strong>🧠 Explainable AI (XAI) Insight</strong>
                                <p style={{ lineHeight: 1.8 }}>
                                    {movie.reason || `TF-IDF Content Match: This movie scored high on cosine similarity based on overlapping genre (${movie.genre}) and mood (${movie.mood}) feature vectors from your preference profile.`}
                                </p>
                            </div>
                        )}

                        {/* Action Buttons */}
                        <div className="action-buttons" style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
                            {onToggleWatchlist && (
                                <button className={`add-watchlist-btn ${inWatchlist ? 'in-watchlist' : ''}`} onClick={onToggleWatchlist}>
                                    {inWatchlist ? "✓ In Watchlist" : "+ Watchlist"}
                                </button>
                            )}

                            {movie.trailer_embed && (
                                <button className="trailer-btn" onClick={() => setShowTrailer(!showTrailer)}>
                                    {showTrailer ? '✕ Hide Trailer' : '▶ Watch Trailer'}
                                </button>
                            )}

                            {onSubmitRating && (
                                <div className="rating-input" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                    <input
                                        type="number"
                                        min="1" max="10" step="0.5"
                                        placeholder="Rate 1-10"
                                        className="input-field"
                                        style={{ width: '100px', marginBottom: 0, padding: '0.5rem 1rem' }}
                                        value={rating}
                                        onChange={(e) => setRating(e.target.value)}
                                    />
                                    <button className="ott-button" style={{ padding: '0.5rem 1rem' }} onClick={handleRating}>
                                        ⭐ Rate
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* YouTube Trailer */}
                        {showTrailer && movie.trailer_embed && (
                            <div className="trailer-container" style={{ marginTop: '1.5rem' }}>
                                <iframe
                                    width="100%"
                                    height="280"
                                    src={movie.trailer_embed}
                                    title={`${movie.title} Trailer`}
                                    frameBorder="0"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                    style={{ borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}
                                ></iframe>
                            </div>
                        )}
                    </div>
                </div>

                {/* Similar Movies (Hybrid Recommendations) */}
                {hybridRecs && hybridRecs.length > 0 && (
                    <div className="modal-similar" style={{ padding: '2rem 2rem 2rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3 style={{ color: '#fff', fontSize: '1.3rem' }}>🤝 More Like This (Hybrid AI)</h3>
                            <span className="algo-badge">Content 60% + Collaborative 40%</span>
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                            {hybridRecs.slice(0, 6).map(rec => (
                                <div key={`sim-${rec.id}`} style={{ flex: '0 0 160px' }}>
                                    <MovieCard movie={rec} onClick={(m) => { onClose(); setTimeout(() => onMovieClick && onMovieClick(m), 100); }} />
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
