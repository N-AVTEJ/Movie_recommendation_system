"""
CineIndia - Complete Flask Backend
====================================
All API endpoints for the movie recommendation system.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import base64
import numpy as np
import cv2

# (Emotion engine removed per user request)

from recommendation import (
    fetch_movies_df, get_recommendations, get_db_connection,
    get_content_recommendations, get_collaborative_recommendations,
    get_hybrid_recommendations, get_recommendations_by_mood,
    natural_language_search, get_tmdb_trending, get_tmdb_movie_details,
    get_tmdb_trailer, get_diverse_recommendations, cold_start_recommendations,
    get_user_taste_profile, get_xai_explanation
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ─────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "CineIndia API", "version": "3.0.0"}), 200


# ─────────────────────────────────────────────────────────────
# MOVIES CRUD
# ─────────────────────────────────────────────────────────────

@app.route('/movies', methods=['GET'])
def get_movies():
    df = fetch_movies_df()
    if df.empty:
        return jsonify({"movies": []}), 200
    # Drop heavy TF-IDF column before sending
    df = df.drop(columns=['combined_text'], errors='ignore')
    movies = df.fillna("").to_dict(orient='records')
    return jsonify({"movies": movies}), 200


@app.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    df = fetch_movies_df()
    if df.empty:
        return jsonify({"error": "No movies found"}), 404

    movie = df[df['id'] == movie_id].drop(columns=['combined_text'], errors='ignore')
    if movie.empty:
        return jsonify({"error": "Movie not found"}), 404

    movie_dict = movie.fillna("").to_dict(orient='records')[0]

    # Enrich with TMDB trailer if possible
    try:
        trailer = get_tmdb_trailer(movie_dict.get('title', ''), movie_dict.get('release_year'))
        if trailer:
            movie_dict['trailer_embed'] = trailer
    except Exception:
        pass

    return jsonify(movie_dict), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 1: CONTENT-BASED RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────

@app.route('/recommend', methods=['POST'])
def recommend():
    """Content-based: recommend similar movies using TF-IDF cosine similarity."""
    data = request.json
    if not data or 'movie_id' not in data:
        return jsonify({"error": "movie_id is required"}), 400

    movie_id = int(data.get('movie_id'))
    top_n = int(data.get('top_n', 5))

    recs = get_content_recommendations(movie_id, top_n=top_n)
    # Clean complex objects
    cleaned = _clean_recs(recs)
    return jsonify({"recommendations": cleaned, "type": "content-based", "algorithm": "TF-IDF Cosine Similarity"}), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 2: COLLABORATIVE FILTERING
# ─────────────────────────────────────────────────────────────

@app.route('/recommend/collaborative', methods=['POST'])
def recommend_collaborative():
    """SVD-based collaborative filtering recommendations."""
    data = request.json
    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400

    user_id = int(data.get('user_id'))
    top_n = int(data.get('top_n', 10))

    recs = get_collaborative_recommendations(user_id, top_n=top_n)
    cleaned = _clean_recs(recs)
    return jsonify({"recommendations": cleaned, "type": "collaborative", "algorithm": "SVD Matrix Factorization"}), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 3: HYBRID RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────

@app.route('/recommend/hybrid', methods=['POST'])
def recommend_hybrid():
    """Hybrid: blend content-based (60%) + collaborative (40%)."""
    data = request.json
    if not data or 'movie_id' not in data:
        return jsonify({"error": "movie_id is required"}), 400

    movie_id = int(data.get('movie_id'))
    user_id = data.get('user_id')
    if user_id:
        user_id = int(user_id)
    top_n = int(data.get('top_n', 10))

    recs = get_hybrid_recommendations(movie_id, user_id=user_id, top_n=top_n)
    cleaned = _clean_recs(recs)
    return jsonify({"recommendations": cleaned, "type": "hybrid", "algorithm": "Content (60%) + Collaborative (40%)"}), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 4: MOOD-BASED RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────

@app.route('/mood', methods=['POST'])
def mood_recommendation():
    """Mood-based recommendations with VADER sentiment analysis."""
    data = request.json
    if not data or 'mood' not in data:
        return jsonify({"error": "mood is required"}), 400

    mood = data.get('mood')
    top_n = int(data.get('top_n', 8))

    recs = get_recommendations_by_mood(mood, top_n=top_n)
    cleaned = _clean_recs(recs)
    return jsonify({
        "recommendations": cleaned,
        "mood": mood,
        "type": "mood-based",
        "algorithm": "Genre Mapping + VADER Sentiment Analysis"
    }), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 5: EXPLAINABLE AI
# ─────────────────────────────────────────────────────────────

@app.route('/explain', methods=['POST'])
def explain():
    """Get XAI explanation for why a movie was recommended."""
    data = request.json
    movie_id = data.get('movie_id')
    compared_to_id = data.get('compared_to_id')

    if not movie_id or not compared_to_id:
        return jsonify({"error": "movie_id and compared_to_id are required"}), 400

    explanation = get_xai_explanation(int(movie_id), int(compared_to_id))
    return jsonify({"explanation": explanation, "type": "XAI", "algorithm": "NLP Feature Comparison"}), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 6: NATURAL LANGUAGE SEARCH (NLP)
# ─────────────────────────────────────────────────────────────

@app.route('/search/natural', methods=['POST'])
def nl_search():
    """Natural language search: 'I want a movie like Interstellar but more emotional'."""
    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"error": "query is required"}), 400

    top_n = int(data.get('top_n', 10))
    results = natural_language_search(query, top_n=top_n)
    cleaned = _clean_recs(results)

    return jsonify({
        "results": cleaned,
        "query": query,
        "type": "nlp-search",
        "algorithm": "TF-IDF + VADER Sentiment Alignment"
    }), 200


@app.route('/search', methods=['GET'])
def search():
    """Basic text search by title (legacy support)."""
    query = request.args.get('q', '').lower()
    df = fetch_movies_df()
    if df.empty:
        return jsonify({"movies": []}), 200

    filtered = df[df['title'].str.lower().str.contains(query, na=False)]
    movies = filtered.drop(columns=['combined_text'], errors='ignore').fillna("").to_dict(orient='records')
    return jsonify({"movies": movies}), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 7: REAL-TIME TRENDING (TMDB)
# ─────────────────────────────────────────────────────────────

@app.route('/trending', methods=['GET'])
def trending():
    """Fetch real-time trending movies from TMDB API."""
    page = int(request.args.get('page', 1))
    results = get_tmdb_trending(page)

    # If TMDB fails, return top-rated local movies
    if not results:
        df = fetch_movies_df()
        if not df.empty:
            top = df.nlargest(10, 'rating').drop(columns=['combined_text'], errors='ignore')
            movies = top.fillna("").to_dict(orient='records')
            for m in movies:
                m['reason'] = "🔥 Local Trending: Top-rated in our catalog."
            return jsonify({"trending": movies, "source": "local_fallback"}), 200
        return jsonify({"trending": []}), 200

    return jsonify({"trending": results, "source": "tmdb"}), 200


@app.route('/tmdb/details/<int:tmdb_id>', methods=['GET'])
def tmdb_details(tmdb_id):
    """Get TMDB movie details including YouTube trailer."""
    details = get_tmdb_movie_details(tmdb_id)
    return jsonify(details), 200


@app.route('/movie/<int:movie_id>/trailer', methods=['GET'])
def get_trailer(movie_id):
    """Get YouTube trailer for a local movie via TMDB search."""
    df = fetch_movies_df()
    movie = df[df['id'] == movie_id]
    if movie.empty:
        return jsonify({"trailer": None}), 404

    row = movie.iloc[0]
    trailer = get_tmdb_trailer(row['title'], row.get('release_year'))
    return jsonify({"trailer_embed": trailer, "movie_id": movie_id}), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 8: DIVERSITY-AWARE RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────

@app.route('/recommend/diverse', methods=['POST'])
def recommend_diverse():
    """Diversity-aware recommendations using MMR algorithm."""
    data = request.json or {}
    movie_id = data.get('movie_id')
    user_id = data.get('user_id')
    top_n = int(data.get('top_n', 10))

    if movie_id:
        movie_id = int(movie_id)
    if user_id:
        user_id = int(user_id)

    recs = get_diverse_recommendations(movie_id=movie_id, user_id=user_id, top_n=top_n)
    cleaned = _clean_recs(recs)
    return jsonify({
        "recommendations": cleaned,
        "type": "diversity-aware",
        "algorithm": "Maximal Marginal Relevance (MMR)"
    }), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 9: COLD START / ONBOARDING QUIZ
# ─────────────────────────────────────────────────────────────

@app.route('/onboarding/quiz', methods=['POST'])
def onboarding_quiz():
    """
    Cold-start onboarding quiz.
    Accepts favorite genres and moods to build instant taste profile.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Quiz data required"}), 400

    favorite_genres = data.get('genres', [])
    favorite_moods = data.get('moods', [])
    user_id = data.get('user_id')
    top_n = int(data.get('top_n', 10))

    # Get cold-start recommendations
    recs = cold_start_recommendations(favorite_genres, favorite_moods, top_n=top_n)
    cleaned = _clean_recs(recs)

    # Optionally save preferences to user profile
    if user_id:
        prefs_str = ', '.join(favorite_genres + favorite_moods)
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET preferences = %s WHERE id = %s",
                    (prefs_str, int(user_id))
                )
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error saving quiz prefs: {e}")

    return jsonify({
        "recommendations": cleaned,
        "type": "cold-start",
        "algorithm": "Onboarding Quiz → Genre/Mood Matching + MMR Diversity",
        "profile": {"genres": favorite_genres, "moods": favorite_moods}
    }), 200


# ─────────────────────────────────────────────────────────────
# FEATURE 10: USER TASTE PROFILE DASHBOARD
# ─────────────────────────────────────────────────────────────

@app.route('/user/<int:user_id>/profile', methods=['GET'])
def user_profile(user_id):
    """Get user's complete taste profile for dashboard visualization."""
    profile = get_user_taste_profile(user_id)
    return jsonify(profile), 200


# ─────────────────────────────────────────────────────────────
# AUTH ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    preferences = data.get('preferences', '')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB error"}), 500
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, preferences) VALUES (%s, %s, %s)",
            (username, password, preferences)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return jsonify({"message": "User created", "user_id": user_id, "username": username}), 201
    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({"error": "Username already exists"}), 409
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB error"}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, preferences FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"message": "Login successful", "user": user}), 200
    return jsonify({"error": "Invalid credentials"}), 401


# ─────────────────────────────────────────────────────────────
# WATCHLIST & RATINGS
# ─────────────────────────────────────────────────────────────

@app.route('/watchlist', methods=['POST', 'GET'])
def watchlist():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB error"}), 500
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        movie_id = data.get('movie_id')

        cursor.execute("SELECT id FROM watchlists WHERE user_id = %s AND movie_id = %s", (user_id, movie_id))
        if cursor.fetchone():
            cursor.execute("DELETE FROM watchlists WHERE user_id = %s AND movie_id = %s", (user_id, movie_id))
            action = "removed"
        else:
            cursor.execute("INSERT INTO watchlists (user_id, movie_id) VALUES (%s, %s)", (user_id, movie_id))
            action = "added"
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Movie {action} successfully", "action": action}), 200

    elif request.method == 'GET':
        user_id = request.args.get('user_id')
        cursor.execute('''
            SELECT m.* FROM movies m
            JOIN watchlists w ON m.id = w.movie_id
            WHERE w.user_id = %s
        ''', (user_id,))
        movies = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"watchlist": movies}), 200


@app.route('/rate', methods=['POST'])
def rate_movie():
    data = request.json
    user_id = data.get('user_id')
    movie_id = data.get('movie_id')
    rating = data.get('rating')

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB error"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user_ratings WHERE user_id = %s AND movie_id = %s", (user_id, movie_id))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE user_ratings SET rating = %s WHERE user_id = %s AND movie_id = %s",
            (rating, user_id, movie_id)
        )
    else:
        cursor.execute(
            "INSERT INTO user_ratings (user_id, movie_id, rating) VALUES (%s, %s, %s)",
            (user_id, movie_id, rating)
        )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Rating saved"}), 200


@app.route('/ratings/<int:user_id>', methods=['GET'])
def get_user_ratings(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"ratings": []}), 200
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT movie_id, rating FROM user_ratings WHERE user_id = %s",
        (user_id,)
    )
    ratings = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"ratings": ratings}), 200


# (Emotion endpoints removed)

# ─────────────────────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────

def _clean_recs(recs):
    """Clean recommendation list: handle NaN, convert numpy types."""
    cleaned = []
    for r in recs:
        clean = {}
        for k, v in r.items():
            if hasattr(v, 'item'):
                clean[k] = v.item()
            elif v != v:  # NaN check
                clean[k] = ""
            else:
                clean[k] = v
        cleaned.append(clean)
    return cleaned


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
