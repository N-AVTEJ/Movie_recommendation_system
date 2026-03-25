"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:5000';

const GENRE_OPTIONS = ['Action', 'Drama', 'Comedy', 'Romance', 'Thriller', 'Biography', 'Crime', 'Fantasy', 'Horror', 'Animation', 'Sport', 'Musical'];
const MOOD_OPTIONS = ['Happy', 'Sad', 'Romantic', 'Thrilled', 'Motivational', 'Action'];

export default function Login() {
    const router = useRouter();
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [step, setStep] = useState(1); // 1: credentials, 2: quiz

    // Quiz state (Cold Start)
    const [selectedGenres, setSelectedGenres] = useState([]);
    const [selectedMoods, setSelectedMoods] = useState([]);

    const toggleGenre = (g) => setSelectedGenres(prev =>
        prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g]
    );
    const toggleMood = (m) => setSelectedMoods(prev =>
        prev.includes(m) ? prev.filter(x => x !== m) : [...prev, m]
    );

    const handleCredentials = (e) => {
        e.preventDefault();
        setError('');
        if (!username.trim() || !password) {
            setError('Username and password are required');
            return;
        }
        if (!isLogin) {
            setStep(2); // Go to quiz for registration
        } else {
            handleLogin();
        }
    };

    const handleLogin = async () => {
        setError('');
        try {
            const res = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Login failed');
            localStorage.setItem('user', JSON.stringify(data.user));
            router.push('/dashboard');
        } catch (err) {
            setError(err.message);
        }
    };

    const handleRegisterWithQuiz = async () => {
        setError('');
        const preferences = [...selectedGenres, ...selectedMoods].join(', ');

        try {
            // Register
            const res = await fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, preferences })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Registration failed');

            const user = { id: data.user_id, username, preferences };
            localStorage.setItem('user', JSON.stringify(user));

            // Save quiz preferences via onboarding quiz endpoint
            if (selectedGenres.length > 0 || selectedMoods.length > 0) {
                await fetch(`${API_BASE}/onboarding/quiz`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: data.user_id,
                        genres: selectedGenres,
                        moods: selectedMoods,
                        top_n: 10
                    })
                });
            }

            router.push('/dashboard');
        } catch (err) {
            setError(err.message);
            setStep(1);
        }
    };

    return (
        <div className="login-page">
            <div className="login-bg-effects">
                <div className="bg-circle bg-circle-1"></div>
                <div className="bg-circle bg-circle-2"></div>
                <div className="bg-circle bg-circle-3"></div>
            </div>

            <div className="login-container">
                {/* Logo */}
                <div className="login-logo">
                    <span className="logo-icon">🎬</span>
                    <span className="logo-text">CineIndia</span>
                </div>

                <div className="login-card glassmorphism">
                    {/* STEP 1: CREDENTIALS */}
                    {step === 1 && (
                        <>
                            <h2 className="login-title">
                                {isLogin ? 'Welcome Back 👋' : 'Join CineIndia 🎬'}
                            </h2>
                            <p className="login-subtitle">
                                {isLogin
                                    ? 'Sign in to your personalized movie universe'
                                    : 'Create your account to get AI-powered recommendations'}
                            </p>

                            {error && <div className="error-box">{error}</div>}

                            <form onSubmit={handleCredentials} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
                                <div className="input-group">
                                    <span className="input-icon">👤</span>
                                    <input
                                        type="text"
                                        placeholder="Username"
                                        required
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        className="input-field"
                                    />
                                </div>
                                <div className="input-group">
                                    <span className="input-icon">🔒</span>
                                    <input
                                        type="password"
                                        placeholder="Password"
                                        required
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="input-field"
                                    />
                                </div>

                                <button type="submit" className="ott-button" style={{ width: '100%', fontSize: '1.1rem', padding: '1rem' }}>
                                    {isLogin ? '🚀 Login' : '➡️ Next: Choose Preferences'}
                                </button>
                            </form>

                            <p style={{ textAlign: 'center', marginTop: '1.5rem', color: '#aaa' }}>
                                {isLogin ? "New here? " : "Already have an account? "}
                                <span
                                    style={{ color: 'var(--accent)', cursor: 'pointer', fontWeight: 700 }}
                                    onClick={() => { setIsLogin(!isLogin); setStep(1); setError(''); }}
                                >
                                    {isLogin ? 'Sign Up' : 'Login'}
                                </span>
                            </p>
                        </>
                    )}

                    {/* STEP 2: COLD START QUIZ */}
                    {step === 2 && (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                <button onClick={() => setStep(1)} style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', borderRadius: '50%', width: 36, height: 36, cursor: 'pointer', fontSize: '1rem' }}>←</button>
                                <div>
                                    <h2 className="login-title" style={{ margin: 0 }}>🎯 Taste Quiz</h2>
                                    <p style={{ color: '#aaa', fontSize: '0.85rem', marginTop: '0.2rem' }}>Cold Start — no history needed!</p>
                                </div>
                            </div>

                            <div className="feature-banner cold-start" style={{ marginBottom: '1.5rem' }}>
                                <span className="feature-icon">❄️</span>
                                <div>
                                    <strong>Why this quiz?</strong>
                                    <p style={{ fontSize: '0.85rem' }}>As a new user you have no watch history. Your quiz answers instantly build a taste profile to power personalized recommendations from day one.</p>
                                </div>
                            </div>

                            {error && <div className="error-box">{error}</div>}

                            <div style={{ marginBottom: '1.5rem' }}>
                                <h4 style={{ marginBottom: '0.8rem', color: '#ddd' }}>🎬 Pick your favorite genres (choose 3+):</h4>
                                <div className="quiz-chips">
                                    {GENRE_OPTIONS.map(g => (
                                        <button
                                            key={g}
                                            className={`quiz-chip ${selectedGenres.includes(g) ? 'selected' : ''}`}
                                            onClick={() => toggleGenre(g)}
                                            type="button"
                                        >
                                            {g} {selectedGenres.includes(g) ? '✓' : '+'}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div style={{ marginBottom: '2rem' }}>
                                <h4 style={{ marginBottom: '0.8rem', color: '#ddd' }}>🎭 What mood do you usually watch in?</h4>
                                <div className="quiz-chips">
                                    {MOOD_OPTIONS.map(m => (
                                        <button
                                            key={m}
                                            className={`quiz-chip mood-quiz-chip ${selectedMoods.includes(m) ? 'selected' : ''}`}
                                            onClick={() => toggleMood(m)}
                                            type="button"
                                        >
                                            {m} {selectedMoods.includes(m) ? '✓' : '+'}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {selectedGenres.length > 0 && (
                                <div style={{ marginBottom: '1rem', padding: '0.8rem', background: 'rgba(0,210,255,0.05)', borderRadius: '8px', border: '1px solid rgba(0,210,255,0.2)' }}>
                                    <small style={{ color: '#00d2ff' }}>
                                        ✓ Selected: {[...selectedGenres, ...selectedMoods].join(', ')}
                                    </small>
                                </div>
                            )}

                            <button
                                className="ott-button"
                                style={{ width: '100%', fontSize: '1.1rem', padding: '1rem' }}
                                onClick={handleRegisterWithQuiz}
                            >
                                🎬 Create My Taste Profile
                            </button>

                            <p style={{ textAlign: 'center', marginTop: '1rem' }}>
                                <span
                                    style={{ color: '#aaa', cursor: 'pointer', fontSize: '0.9rem' }}
                                    onClick={handleRegisterWithQuiz}
                                >
                                    Skip quiz →
                                </span>
                            </p>
                        </>
                    )}
                </div>

                <div className="login-features">
                    {[
                        { icon: '🧠', label: 'AI Recommendations' },
                        { icon: '🎭', label: 'Mood Engine' },
                        { icon: '📷', label: 'Emotion Detection' },
                        { icon: '🔥', label: 'Live Trending' },
                    ].map(f => (
                        <div key={f.label} className="feature-pill">
                            <span>{f.icon}</span> {f.label}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
