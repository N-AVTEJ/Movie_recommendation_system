export default function MovieCard({ movie, onClick }) {
    // Mood badge color map
    const moodColors = {
        Happy: '#FFD700', Sad: '#6495ED', Romantic: '#FF69B4',
        Action: '#FF6B35', Motivational: '#32CD32', Neutral: '#888',
        Angry: '#FF4500', Thrilled: '#FF4500',
    };
    const moodColor = moodColors[movie.mood] || '#888';

    return (
        <div
            className="movie-card glassmorphism"
            onClick={() => {
                console.log("Selection Trace - Card Clicked:", movie.title, movie.id);
                onClick(movie);
            }}
        >
            <div className="movie-poster-container">
                <img
                    src={movie.poster_url}
                    alt={movie.title}
                    className="movie-poster"
                    onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = 'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=300&h=450&auto=format&fit=crop';
                    }}
                />
                <div className="ott-badge" title={`Available on ${movie.ott_platform}`}>
                    {movie.ott_platform}
                </div>
                {movie.mood && (
                    <div
                        className="mood-badge"
                        style={{ background: moodColor }}
                        title={`${movie.mood} mood`}
                    >
                        {movie.mood}
                    </div>
                )}
            </div>
            <div className="movie-info">
                <h3>{movie.title}</h3>
                <p className="genre">{movie.genre}</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div className="rating">⭐ {movie.rating}/10</div>
                    {movie.release_year && (
                        <span style={{ color: '#888', fontSize: '0.8rem' }}>{movie.release_year}</span>
                    )}
                </div>
                {movie.cast_members && (
                    <p style={{ color: '#aaa', fontSize: '0.78rem', marginTop: '0.25rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {movie.cast_members}
                    </p>
                )}
            </div>
        </div>
    );
}
