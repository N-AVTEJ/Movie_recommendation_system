"""
CineIndia - Complete ML Recommendation Engine
=========================================================
Features implemented:
1. Content-Based Filtering: TF-IDF + Cosine Similarity on genres, descriptions, cast
2. Collaborative Filtering: SVD via matrix factorization (scipy)
3. Hybrid Recommendations: Weighted blend of content + collaborative scores
4. Mood-Based Recommendations: Genre mapping + VADER sentiment analysis
5. Explainable AI (XAI): NLP-driven reason generation using description analysis
6. Natural Language Search: TF-IDF semantic search on descriptions
7. Diversity-Aware Recommendations: MMR (Maximal Marginal Relevance) for filter bubble avoidance
8. Cold Start Solution: Onboarding quiz using genre preference matching
9. Real-Time Trending: TMDB API integration (with local fallback)
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import mysql.connector
import requests
import os
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ─── DB CONNECTION ─────────────────────────────────────────────────────────────

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'movie_recommendation_db'
}

TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '4f4d75e42e3b3a8d0a35c9fa56d1c4e1')

MOOD_GENRE_MAP = {
    'Happy':        ['Comedy', 'Family', 'Animation', 'Musical', 'Adventure'],
    'Sad':          ['Drama', 'Romance', 'Biography', 'Mystery', 'Crime'],
    'Romantic':     ['Romance', 'Drama', 'Musical'],
    'Thrilled':     ['Thriller', 'Horror', 'Mystery', 'Crime'],
    'Action':       ['Action', 'Adventure', 'War', 'Crime', 'Thriller'],
    'Motivational': ['Biography', 'Sport', 'Drama', 'War', 'Adventure'],
    'Scary':        ['Horror', 'Thriller', 'Mystery'],
    'Neutral':      ['Drama', 'Biography', 'Sport', 'Adventure', 'Comedy'],
    'Angry':        ['Action', 'Thriller', 'Crime', 'Drama'],
    'Fearful':      ['Drama', 'Mystery', 'Crime', 'Thriller'],
    'Surprised':    ['Comedy', 'Adventure', 'Action', 'Mystery'],
}

vader_analyzer = SentimentIntensityAnalyzer()

# ─── LOAD OPTIMIZED HYPERPARAMETERS (from train_models.py output) ──────────────
# Run `python train_models.py` to generate model_params.json
_PARAMS_FILE = os.path.join(os.path.dirname(__file__), 'model_params.json')
_OPTIMIZED_PARAMS = {}

try:
    import json as _json
    if os.path.exists(_PARAMS_FILE):
        with open(_PARAMS_FILE, 'r') as _f:
            _OPTIMIZED_PARAMS = _json.load(_f).get('features', {})
        print(f"[recommendation.py] ✅ Loaded optimized params from model_params.json")
        print(f"[recommendation.py]    Overall trained accuracy: "
              f"{_json.load(open(_PARAMS_FILE)).get('overall_accuracy', 'N/A')}%")
    else:
        print("[recommendation.py] ℹ️  No model_params.json found — using defaults. "
              "Run python train_models.py to optimize.")
except Exception as _e:
    print(f"[recommendation.py] ⚠️  Could not load model_params.json: {_e}")

# Extract individual optimized params with safe defaults
_CONTENT_PARAMS  = _OPTIMIZED_PARAMS.get('content_based', {})
_COLLAB_PARAMS   = _OPTIMIZED_PARAMS.get('collaborative_filtering', {})
_HYBRID_PARAMS   = _OPTIMIZED_PARAMS.get('hybrid', {})
_MMR_PARAMS      = _OPTIMIZED_PARAMS.get('diversity_mmr', {})

CONTENT_NGRAM    = tuple(_CONTENT_PARAMS.get('ngram_range', [1, 2]))
CONTENT_MAXFEAT  = _CONTENT_PARAMS.get('max_features', 5000)
CONTENT_SUBLIN   = _CONTENT_PARAMS.get('sublinear_tf', True)
SVD_K            = _COLLAB_PARAMS.get('svd_k', 20)
HYBRID_W_CONTENT = _HYBRID_PARAMS.get('content_weight', 0.6)
HYBRID_W_COLLAB  = _HYBRID_PARAMS.get('collab_weight', 0.4)
MMR_LAMBDA       = _MMR_PARAMS.get('mmr_lambda', 0.5)



def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"DB Error: {e}")
        return None


# ─── DATA FETCHING ─────────────────────────────────────────────────────────────

def fetch_movies_df():
    """Fetch all movies from DB and build combined text feature."""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame()
        df = pd.read_sql("SELECT * FROM movies", conn)
        conn.close()

        # Build rich combined feature for TF-IDF
        df['combined_text'] = (
            df['genre'].fillna('') + ' ' +
            df['description'].fillna('') + ' ' +
            df['cast_members'].fillna('') + ' ' +
            df['mood'].fillna('') + ' ' +
            df['genre'].fillna('')  # weight genre twice
        )
        return df
    except Exception as e:
        print(f"Error fetching movies: {e}")
        return pd.DataFrame()


def fetch_user_ratings():
    """Fetch all user ratings from DB."""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame()
        df = pd.read_sql("SELECT user_id, movie_id, rating FROM user_ratings", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching ratings: {e}")
        return pd.DataFrame()


# ─── FEATURE 1: CONTENT-BASED FILTERING (TF-IDF) ──────────────────────────────

def build_content_similarity_matrix(df):
    """Build TF-IDF cosine similarity matrix using optimized hyperparameters."""
    tfidf = TfidfVectorizer(
        stop_words='english',
        ngram_range=CONTENT_NGRAM,
        max_features=CONTENT_MAXFEAT,
        sublinear_tf=CONTENT_SUBLIN
    )
    tfidf_matrix = tfidf.fit_transform(df['combined_text'])
    similarity = cosine_similarity(tfidf_matrix)
    return similarity, tfidf, tfidf_matrix


def get_content_recommendations(movie_id, df=None, top_n=10):
    """Content-based recommendations for a movie using TF-IDF cosine similarity."""
    if df is None:
        df = fetch_movies_df()
    if df.empty:
        return []

    sim_matrix, _, _ = build_content_similarity_matrix(df)

    matches = df[df['id'] == movie_id]
    if matches.empty:
        return []
    movie_index = matches.index[0]

    # Get similarity scores
    sim_scores = list(enumerate(sim_matrix[movie_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    results = []
    source_movie = df.iloc[movie_index]

    for idx, sim_score in sim_scores:
        if df.iloc[idx]['id'] == movie_id:
            continue
        movie_row = df.iloc[idx].to_dict()
        movie_row['content_score'] = float(sim_score)
        movie_row['reason'] = _generate_xai_reason(source_movie, df.iloc[idx])
        results.append(movie_row)
        if len(results) >= top_n:
            break

    return results


# ─── FEATURE 2: COLLABORATIVE FILTERING (SVD-STYLE) ──────────────────────────

def get_collaborative_recommendations(user_id, df=None, top_n=10):
    """
    Collaborative filtering using matrix factorization (SVD via scipy).
    Falls back to popularity if user has no ratings.
    """
    if df is None:
        df = fetch_movies_df()
    ratings_df = fetch_user_ratings()

    if df.empty:
        return []

    if ratings_df.empty or user_id not in ratings_df['user_id'].values:
        # Cold start: return top-rated movies
        return _cold_start_popular(df, top_n)

    # Build user-item matrix
    all_user_ids = ratings_df['user_id'].unique()
    all_movie_ids = df['id'].tolist()

    user_idx = {u: i for i, u in enumerate(all_user_ids)}
    movie_idx = {m: j for j, m in enumerate(all_movie_ids)}

    R = np.zeros((len(all_user_ids), len(all_movie_ids)))
    for _, row in ratings_df.iterrows():
        if row['movie_id'] in movie_idx:
            R[user_idx[row['user_id']], movie_idx[row['movie_id']]] = row['rating']

    # SVD decomposition
    try:
        from scipy.sparse.linalg import svds
        from scipy.sparse import csr_matrix
        R_sparse = csr_matrix(R)
        k = min(SVD_K, min(R.shape) - 1)
        U, sigma, Vt = svds(R_sparse, k=k)
        sigma_diag = np.diag(sigma)
        R_predicted = np.dot(np.dot(U, sigma_diag), Vt)
    except Exception:
        # Fallback: simple mean normalization
        R_predicted = R

    if user_id not in user_idx:
        return _cold_start_popular(df, top_n)

    u_idx = user_idx[user_id]
    user_predictions = R_predicted[u_idx]

    # Get movies user hasn't rated
    rated_movie_ids = set(ratings_df[ratings_df['user_id'] == user_id]['movie_id'].tolist())

    scored = []
    for movie_id, j in movie_idx.items():
        if movie_id not in rated_movie_ids:
            scored.append((movie_id, user_predictions[j]))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_ids = [m[0] for m in scored[:top_n]]

    results = []
    for mid in top_ids:
        row = df[df['id'] == mid]
        if not row.empty:
            d = row.iloc[0].to_dict()
            d['collab_score'] = float(scored[[m[0] for m in scored].index(mid)][1])
            d['reason'] = f"🤝 Collaborative: Users with similar taste highly rated this."
            results.append(d)

    return results


def _cold_start_popular(df, top_n):
    """Return top-rated diverse movies for cold start."""
    top = df.nlargest(top_n * 2, 'rating')
    diverse = _apply_diversity(top, top_n)
    results = []
    for _, row in diverse.iterrows():
        d = row.to_dict()
        d['reason'] = f"🌟 Trending Choice: Highly rated by the CineIndia community."
        results.append(d)
    return results


# ─── FEATURE 3: HYBRID RECOMMENDATION ────────────────────────────────────────

def get_hybrid_recommendations(movie_id, user_id=None, top_n=10):
    """
    Hybrid: weighted blend of content-based (60%) + collaborative (40%).
    Content-based requires a seed movie; collaborative requires user history.
    """
    df = fetch_movies_df()
    if df.empty:
        return []

    content_recs = get_content_recommendations(movie_id, df, top_n=top_n * 2)
    collab_recs = get_collaborative_recommendations(user_id, df, top_n=top_n * 2) if user_id else []

    # Map movie_id → score
    content_scores = {r['id']: r.get('content_score', 0) for r in content_recs}
    collab_scores = {r['id']: r.get('collab_score', 0) for r in collab_recs}

    # Normalize scores to [0,1]
    def normalize(score_dict):
        vals = list(score_dict.values())
        if not vals or max(vals) == 0:
            return score_dict
        mx = max(vals)
        return {k: v / mx for k, v in score_dict.items()}

    content_scores = normalize(content_scores)
    collab_scores = normalize(collab_scores)

    all_ids = set(content_scores.keys()) | set(collab_scores.keys())

    hybrid = {}
    for mid in all_ids:
        cs = content_scores.get(mid, 0)
        co = collab_scores.get(mid, 0)
        hybrid[mid] = cs * HYBRID_W_CONTENT + co * HYBRID_W_COLLAB

    sorted_ids = sorted(hybrid.keys(), key=lambda x: hybrid[x], reverse=True)[:top_n]

    # Merge all rec dicts
    id_to_rec = {r['id']: r for r in content_recs}
    id_to_rec.update({r['id']: r for r in collab_recs})

    results = []
    source_movie = df[df['id'] == movie_id]
    for mid in sorted_ids:
        if mid in id_to_rec:
            rec = id_to_rec[mid].copy()
            rec['hybrid_score'] = round(hybrid[mid], 3)
            # Generate better XAI reason if source movie known
            if not source_movie.empty:
                target = df[df['id'] == mid]
                if not target.empty:
                    rec['reason'] = _generate_xai_reason(source_movie.iloc[0], target.iloc[0])
            results.append(rec)

    return results


# ─── FEATURE 4: MOOD-BASED WITH SENTIMENT ────────────────────────────────────

def get_recommendations_by_mood(mood, top_n=10):
    """
    Mood-based recommendations using genre mapping + VADER sentiment analysis
    on movie descriptions for score boosting.
    """
    df = fetch_movies_df()
    if df.empty:
        return []

    # Map mood to genres
    target_genres = MOOD_GENRE_MAP.get(mood, [mood])

    # Score each movie
    scores = []
    for _, row in df.iterrows():
        genre_score = 0
        movie_genres = [g.strip().lower() for g in row['genre'].split(',')]
        for tg in target_genres:
            if any(tg.lower() in mg for mg in movie_genres):
                genre_score += 1

        # Mood column match
        mood_match = 1.0 if mood.lower() in str(row['mood']).lower() else 0.0

        # VADER sentiment score
        desc = str(row.get('description', ''))
        vader_score = vader_analyzer.polarity_scores(desc)
        sentiment_val = vader_score['compound']  # [-1, 1]

        # Sentiment alignment with mood
        sentiment_boost = 0
        if mood in ('Happy', 'Romantic', 'Motivational') and sentiment_val > 0.1:
            sentiment_boost = sentiment_val
        elif mood in ('Sad', 'Scary') and sentiment_val < -0.1:
            sentiment_boost = abs(sentiment_val)
        elif mood in ('Thrilled', 'Action'):
            sentiment_boost = abs(sentiment_val) * 0.5

        # Rating normalization
        rating_score = float(row.get('rating', 0)) / 10.0

        # Combined score
        total = (genre_score * 0.4) + (mood_match * 0.3) + (sentiment_boost * 0.15) + (rating_score * 0.15)
        scores.append((_, total))

    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [s[0] for s in scores[:top_n] if s[1] > 0]

    if not top_indices:
        top_indices = [s[0] for s in scores[:top_n]]

    results = []
    for idx in top_indices:
        row = df.loc[idx]
        d = row.to_dict()
        d['reason'] = (
            f"🎭 Mood Match: This movie fits your {mood} mood — "
            f"genre alignment with {', '.join(target_genres[:2])} and "
            f"description sentiment supports a {mood.lower()} experience."
        )
        results.append(d)

    return results


# ─── FEATURE 5: EXPLAINABLE AI (XAI) ─────────────────────────────────────────

def _generate_xai_reason(source_movie, target_movie):
    """
    Generate a human-readable XAI explanation for why a movie was recommended.
    Compares genres, mood, cast, description similarity, and rating.
    """
    reasons = []

    source_title = source_movie.get('title', 'the selected movie')
    target_genres = set(g.strip() for g in str(target_movie.get('genre', '')).split(','))
    source_genres = set(g.strip() for g in str(source_movie.get('genre', '')).split(','))
    shared_genres = target_genres & source_genres

    if shared_genres:
        reasons.append(f"shares the {', '.join(list(shared_genres)[:2])} genre")

    # Mood match
    if str(target_movie.get('mood', '')).lower() == str(source_movie.get('mood', '')).lower():
        reasons.append(f"matches the {source_movie.get('mood', '')} mood")

    # Cast overlap
    source_cast = set(c.strip().lower() for c in str(source_movie.get('cast_members', '')).split(','))
    target_cast = set(c.strip().lower() for c in str(target_movie.get('cast_members', '')).split(','))
    shared_cast = source_cast & target_cast
    if shared_cast:
        cast_name = list(shared_cast)[0].title()
        reasons.append(f"features {cast_name}")

    # Rating
    rating = target_movie.get('rating', 0)
    if rating >= 8.0:
        reasons.append(f"is critically acclaimed ({rating}/10)")

    if reasons:
        reason_str = ', '.join(reasons)
        return f"🧠 XAI Insight: Because you liked '{source_title}', this film was recommended — it {reason_str}."
    else:
        return f"🧠 XAI Insight: This movie closely matches the content DNA of '{source_title}' based on TF-IDF feature overlap."


def get_xai_explanation(movie_id, compared_to_id):
    """API endpoint helper: get XAI explanation comparing two movies."""
    df = fetch_movies_df()
    source = df[df['id'] == compared_to_id]
    target = df[df['id'] == movie_id]
    if source.empty or target.empty:
        return "No explanation available."
    return _generate_xai_reason(source.iloc[0], target.iloc[0])


# ─── FEATURE 6: NATURAL LANGUAGE SEARCH ──────────────────────────────────────

def natural_language_search(query, top_n=10):
    """
    Natural language search using TF-IDF on movie descriptions.
    Understands queries like 'mind-bending sci-fi like Inception but emotional'.
    """
    df = fetch_movies_df()
    if df.empty:
        return []

    if not query or not query.strip():
        return []

    # Use VADER to detect query sentiment
    query_sentiment = vader_analyzer.polarity_scores(query)['compound']

    # Build a combined search corpus: title + genre + description + cast
    search_corpus = df.apply(
        lambda r: f"{r.get('title', '')} {r.get('genre', '')} {r.get('description', '')} {r.get('cast_members', '')} {r.get('mood', '')}",
        axis=1
    ).tolist()

    # Fit TF-IDF on corpus + query
    tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), sublinear_tf=True)
    corpus_with_query = search_corpus + [query]
    tfidf_matrix = tfidf.fit_transform(corpus_with_query)

    query_vec = tfidf_matrix[-1]
    movie_vecs = tfidf_matrix[:-1]
    similarities = cosine_similarity(query_vec, movie_vecs).flatten()

    # Boost scores using sentiment alignment
    results = []
    for i, sim in enumerate(similarities):
        row = df.iloc[i]
        desc_sentiment = vader_analyzer.polarity_scores(str(row.get('description', '')))['compound']

        # Sentiment alignment bonus
        sentiment_match = 1 - abs(query_sentiment - desc_sentiment) / 2
        final_score = sim * 0.8 + sentiment_match * 0.2

        results.append((i, final_score))

    results.sort(key=lambda x: x[1], reverse=True)

    output = []
    for idx, score in results[:top_n]:
        row = df.iloc[idx].to_dict()
        row['search_score'] = round(float(score), 3)
        row['reason'] = (
            f"🔍 NL Search: Matched your query '{query[:60]}...' with "
            f"{round(float(score) * 100, 1)}% relevance based on semantic content analysis."
            if len(query) > 60 else
            f"🔍 NL Search: Matched your query '{query}' with "
            f"{round(float(score) * 100, 1)}% relevance based on semantic content analysis."
        )
        output.append(row)

    return output


# ─── FEATURE 7: REAL-TIME TRENDING (TMDB) ────────────────────────────────────

def get_tmdb_trending(page=1):
    """Fetch trending movies from TMDB API and return enriched data."""
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}&page={page}"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = []
        for item in data.get('results', [])[:10]:
            poster = f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}" if item.get('poster_path') else ''
            results.append({
                'id': f"tmdb_{item['id']}",
                'title': item.get('title', 'Unknown'),
                'description': item.get('overview', ''),
                'rating': round(item.get('vote_average', 0), 1),
                'release_year': str(item.get('release_date', ''))[:4],
                'poster_url': poster,
                'genre': 'International',
                'language': item.get('original_language', '').upper(),
                'mood': 'Various',
                'ott_platform': 'TMDB',
                'cast_members': '',
                'tmdb_id': item['id'],
                'reason': f"🔥 TMDB Trending: Currently trending globally this week with {item.get('vote_count', 0):,} votes."
            })
        return results
    except Exception as e:
        print(f"TMDB API Error: {e}")
        return []


def get_tmdb_movie_details(tmdb_id):
    """Get TMDB movie details including trailer."""
    try:
        # Movie details
        details_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
        videos_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key={TMDB_API_KEY}"
        credits_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits?api_key={TMDB_API_KEY}"

        details = requests.get(details_url, timeout=5).json()
        videos = requests.get(videos_url, timeout=5).json()
        credits = requests.get(credits_url, timeout=5).json()

        # Find YouTube trailer
        trailer_key = None
        for v in videos.get('results', []):
            if v.get('site') == 'YouTube' and v.get('type') in ('Trailer', 'Teaser'):
                trailer_key = v['key']
                break

        # Get top cast
        cast = credits.get('cast', [])[:5]
        cast_names = ', '.join(c['name'] for c in cast)

        return {
            'trailer_url': f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None,
            'trailer_embed': f"https://www.youtube.com/embed/{trailer_key}" if trailer_key else None,
            'cast_members': cast_names,
            'tagline': details.get('tagline', ''),
            'runtime': details.get('runtime'),
            'genres': ', '.join(g['name'] for g in details.get('genres', [])),
        }
    except Exception as e:
        print(f"TMDB Details Error: {e}")
        return {}


def get_tmdb_trailer(title, year=None):
    """Search TMDB for a movie by title and get its trailer."""
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(title)}"
        if year:
            search_url += f"&year={year}"
        results = requests.get(search_url, timeout=5).json().get('results', [])
        if not results:
            return None
        tmdb_id = results[0]['id']
        details = get_tmdb_movie_details(tmdb_id)
        return details.get('trailer_embed')
    except Exception:
        return None


# ─── FEATURE 8: DIVERSITY-AWARE RECOMMENDATIONS ──────────────────────────────

def _apply_diversity(df_subset, top_n, lambda_param=0.5):
    """
    Maximal Marginal Relevance (MMR) for diversity.
    Balances relevance vs. diversity to avoid filter bubbles.
    """
    if df_subset.empty or len(df_subset) <= top_n:
        return df_subset

    # Build mini TF-IDF for diversity scoring
    tfidf = TfidfVectorizer(stop_words='english', max_features=500)
    try:
        texts = df_subset['combined_text'].fillna('').tolist()
        vecs = tfidf.fit_transform(texts).toarray()
    except Exception:
        return df_subset.head(top_n)

    # Normalize ratings as relevance
    ratings = df_subset['rating'].fillna(0).values
    if ratings.max() > 0:
        rel = ratings / ratings.max()
    else:
        rel = np.ones(len(ratings))

    selected = []
    remaining = list(range(len(df_subset)))

    while len(selected) < top_n and remaining:
        if not selected:
            # Pick most relevant
            best = max(remaining, key=lambda i: rel[i])
        else:
            # MMR: balance relevance and diversity
            selected_vecs = vecs[selected]
            scores = []
            for i in remaining:
                sim_to_selected = cosine_similarity(vecs[i].reshape(1, -1), selected_vecs).max()
                mmr = lambda_param * rel[i] - (1 - lambda_param) * sim_to_selected
                scores.append((i, mmr))
            best = max(scores, key=lambda x: x[1])[0]

        selected.append(best)
        remaining.remove(best)

    return df_subset.iloc[selected]


def get_diverse_recommendations(movie_id=None, user_id=None, top_n=10):
    """Get diversity-aware hybrid recommendations."""
    df = fetch_movies_df()
    if df.empty:
        return []

    if movie_id:
        candidates = get_content_recommendations(movie_id, df, top_n=top_n * 3)
    else:
        candidates = _cold_start_popular(df, top_n * 3)

    if not candidates:
        return []

    cand_df = pd.DataFrame(candidates)
    if 'combined_text' not in cand_df.columns:
        cand_df['combined_text'] = (
            cand_df['genre'].fillna('') + ' ' +
            cand_df.get('description', pd.Series([''] * len(cand_df))).fillna('')
        )

    diverse = _apply_diversity(cand_df, top_n)

    results = []
    for _, row in diverse.iterrows():
        d = row.to_dict()
        if 'reason' not in d or not d['reason']:
            d['reason'] = f"🎯 Diversity Pick: Chosen to broaden your taste profile beyond your usual genres."
        else:
            d['reason'] += " ✨ Also picked for genre diversity."
        results.append(d)

    return results


# ─── FEATURE 9: COLD START / ONBOARDING QUIZ ─────────────────────────────────

def cold_start_recommendations(favorite_genres, favorite_moods=None, top_n=10):
    """
    Cold start: given a list of preferred genres (and optional moods from quiz),
    return diverse, high-quality movie recommendations.
    """
    df = fetch_movies_df()
    if df.empty:
        return []

    fav_genres = [g.strip().lower() for g in (favorite_genres or [])]
    fav_moods = [m.strip().lower() for m in (favorite_moods or [])]

    scores = []
    for _, row in df.iterrows():
        movie_genres = [g.strip().lower() for g in str(row['genre']).split(',')]
        movie_mood = str(row.get('mood', '')).lower()

        genre_score = sum(1 for fg in fav_genres if any(fg in mg for mg in movie_genres))
        mood_score = sum(1 for fm in fav_moods if fm in movie_mood)
        rating_score = float(row.get('rating', 0)) / 10.0

        total = genre_score * 0.5 + mood_score * 0.3 + rating_score * 0.2
        scores.append((_, total))

    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [s[0] for s in scores[:top_n * 2]]
    candidates = df.loc[top_indices]
    diverse = _apply_diversity(candidates, top_n)

    results = []
    for _, row in diverse.iterrows():
        d = row.to_dict()
        d['reason'] = (
            f"❄️ Cold Start Match: Recommended based on your quiz preferences "
            f"({', '.join(fav_genres[:3])}) — no prior history needed!"
        )
        results.append(d)

    return results


# ─── FEATURE 10: USER TASTE PROFILE (DASHBOARD DATA) ─────────────────────────

def get_user_taste_profile(user_id):
    """
    Build user taste profile from ratings history.
    Returns genre distribution, avg rating, top moods, top cast.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {}

        # Get rated movies with details
        query = """
            SELECT m.genre, m.mood, m.cast_members, m.rating AS movie_rating,
                   ur.rating AS user_rating, m.title, m.release_year
            FROM user_ratings ur
            JOIN movies m ON ur.movie_id = m.id
            WHERE ur.user_id = %s
        """
        df = pd.read_sql(query, conn, params=(user_id,))
        conn.close()

        if df.empty:
            return {'error': 'No rating history yet', 'total_ratings': 0}

        # Genre breakdown
        all_genres = []
        for genres in df['genre'].fillna(''):
            all_genres.extend([g.strip() for g in genres.split(',')])
        genre_counts = pd.Series(all_genres).value_counts().head(8).to_dict()

        # Mood breakdown
        mood_counts = df['mood'].value_counts().head(5).to_dict()

        # Cast analysis
        all_cast = []
        for cast in df['cast_members'].fillna(''):
            all_cast.extend([c.strip() for c in cast.split(',')])
        cast_counts = pd.Series(all_cast).value_counts().head(5).to_dict()

        # Rating stats
        avg_rating = round(float(df['user_rating'].mean()), 2)
        max_rating = int(df['user_rating'].max())
        min_rating = int(df['user_rating'].min())

        # Taste evolution (ratings by year)
        if 'release_year' in df.columns:
            year_pref = df.groupby('release_year')['user_rating'].mean().round(2).to_dict()
        else:
            year_pref = {}

        return {
            'total_ratings': len(df),
            'avg_rating': avg_rating,
            'max_rating': max_rating,
            'min_rating': min_rating,
            'genre_distribution': genre_counts,
            'mood_distribution': mood_counts,
            'top_cast': cast_counts,
            'year_preferences': {str(k): v for k, v in year_pref.items()},
            'top_rated_movies': df.nlargest(5, 'user_rating')[['title', 'user_rating']].to_dict('records')
        }
    except Exception as e:
        print(f"Taste profile error: {e}")
        return {'error': str(e)}


# ─── BACKWARDS COMPAT WRAPPER ─────────────────────────────────────────────────

def get_recommendations(movie_id, top_n=5):
    """Legacy API: content-based recommendations with XAI."""
    return get_content_recommendations(movie_id, top_n=top_n)
