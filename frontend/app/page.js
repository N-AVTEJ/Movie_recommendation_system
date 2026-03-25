"use client";
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import MovieCard from '../components/MovieCard';

const API_BASE = 'http://localhost:5000';

export default function Home() {
  const router = useRouter();
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if logged in, redirect to dashboard if so
    const user = localStorage.getItem('user');
    if (user) {
      router.push('/dashboard');
      return;
    }

    fetchMovies();
  }, [router]);

  const fetchMovies = async () => {
    try {
      const res = await fetch(`${API_BASE}/movies`);
      const data = await res.json();
      setMovies(data.movies || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="flex-header">
        <h1>CineIndia</h1>
        <button className="ott-button" onClick={() => router.push('/login')}>Login / Register</button>
      </header>

      <section className="hero-banner">
        <div className="hero-content">
          <h2>Welcome to the Ultimate Indian Movie Experience</h2>
          <p>Discover personalized recommendations based on your unique taste.</p>
          <button className="mood-btn active" onClick={() => router.push('/login')} style={{ marginTop: '20px' }}>Get Started</button>
        </div>
      </section>

      <section>
        <h2 className="section-title">Trending Now</h2>
        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : (
          <div className="movie-grid">
            {movies.map(movie => (
              <MovieCard
                key={movie.id}
                movie={movie}
                onClick={() => router.push('/login')} // Prompt login for details
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
