# 🎬 CineIndia — AI-Powered Movie Recommendation System
### Foundation Data Science (FDS) Production Project

> **CineIndia** is a production-grade movie recommendation engine that leverages a multi-algorithm approach to solve the most difficult problems in information retrieval: the Cold Start problem, the Filter Bubble and lack of transparency (XAI).

📖 **[Project Navigation Guide](./PROJECT_DETAILS.md)** | ⚛️ **[Technical & Architecture Deep-Dive](./ABOUT_CINEINDIA.md)**

---

## 🌟 Key Project Highlights

| Feature Area | Core Innovation | Libraries Used |
|---|---|---|
| **Content Match** | TF-IDF Vectorization with Bigrams | `scikit-learn` |
| **Social Logic** | SVD Matrix Factorization | `scipy`, `pandas` |
| **Interaction** | NLP Search + Sentiment Analysis | `vaderSentiment` |
| **Vision AI** | Real-time Emotion Detection | `deepface`, `opencv` |
| **Transparancy** | Explainable AI (XAI) Insight | `custom NLP logic` |
| **Diversity** | Maximal Marginal Relevance (MMR) | `numpy` |

---

## 🚀 All 12 AI/ML Features in Detail

### 1. Content-Based Filtering
*   **Library**: `scikit-learn (TfidfVectorizer, cosine_similarity)`
*   **Logic**: Analyzes the "Content DNA" of movies. We build a high-dimensional vector space representing genres, cast, description, and keywords. When you view a movie, we find the closest neighbor using Cosine Similarity.
*   **Feature Goal**: To find "More Like This" accurately based on plot and cast.

### 2. Collaborative Filtering (Matrix Factorization)
*   **Library**: `scipy.sparse.linalg.svds`
*   **Logic**: Uses **SVD (Singular Value Decomposition)** to decompose the sparse user-rating matrix. It uncovers latent factors (hidden traits) shared between users to predict ratings for movies you haven't seen yet.
*   **Feature Goal**: To provide "Social" recommendations based on similar user tastes.

### 3. Hybrid AI Engine
*   **Library**: `numpy`, `pandas`
*   **Logic**: An ensemble model that calculates a weighted score: **60% Content-based + 40% Collaborative**.
*   **Feature Goal**: Balances accuracy (similarity) with discovery (social trends).

### 4. Mood Engine (Sentiment Analysis)
*   **Library**: `vaderSentiment (SentimentIntensityAnalyzer)`
*   **Logic**: Maps 10+ moods (Happy, Sad, Angry, etc.) to specific genres and then scores the descriptions of those movies using **VADER** to ensure the emotional tone matches your request.
*   **Feature Goal**: Recommending movies that match how you *feel* right now.

### 5. Emotion Recognition via Webcam
*   **Library**: `deepface`, `opencv-python`
*   **Logic**: Captures a frame from your webcam, uses **OpenCV** to detect faces, and **DeepFace** (Convolutional Neural Network) to classify 7 distinct human emotions with confidence scores.
*   **Feature Goal**: Auto-detecting mood to suggest movies without manual input.
*   **Note**: Available as standalone feature at `backend/emotion_detection_page.py`

### 6. Explainable AI (XAI) Insight
*   **Library**: `Custom Python Logic`
*   **Logic**: Breaks down the AI's decision-making process into human-readable reasons by comparing feature overlaps (genre, cast, mood) between the liked movie and the recommendation.
*   **Feature Goal**: Building user trust by explaining the "Why?".

### 7. Natural Language Search (NLP)
*   **Library**: `scikit-learn`, `vaderSentiment`
*   **Logic**: Transforms a free-text query (e.g., *"inspiring sports movies with emotional music"*) into a vector and finds movies whose descriptions align both semantically and emotionally.
*   **Feature Goal**: Allowing conversational search instead of rigid keywords.

### 8. Real-Time Trending (TMDB Integration)
*   **Library**: `requests`
*   **Logic**: Dynamically fetches the current global trending list from **TheMovieDB API**. It injects live metadata into our local Netflix-style UI.
*   **Feature Goal**: Keeping the app fresh with current global cinema trends.

### 9. Cold Start Solution (Onboarding Quiz)
*   **Library**: `Custom Preference Logic`
*   **Logic**: Solves the "new user" problem where the AI has no data. A 2-step onboarding quiz builds an immediate taste profile which the Content-based engine uses as an anchor.
*   **Feature Goal**: Providing high-quality picks on the very first login.

### 10. Diversity-Aware Recs (MMR)
*   **Library**: `numpy`
*   **Logic**: Implements **Maximal Marginal Relevance (MMR)**. It mathematically penalizes redundant entries to ensure your feed has a healthy mix of different genres and eras.
*   **Feature Goal**: Avoiding "Filter Bubbles" where the user only sees one type of movie.

### 11. User Profile Visual Analytics
*   **Library**: `Next.js`, `Vanilla CSS`
*   **Logic**: Aggregates all user interactions (ratings, watchlist) and calculates distribution percentages.
*   **Feature Goal**: Visualizing your movie evolution and most-watched genres.

### 12. Netflix-Style Glassmorphism UI
*   **Tech**: `Next.js 16`, `Vanilla CSS`
*   **Logic**: High-end UX design featuring dark mode, glassmorphism, smooth animations, and interactive trailer overlays via YouTube/TMDB.
*   **Feature Goal**: Providing a commercial-grade, "Wow" factor interface.

---

## 🏗️ Architecture & Tech Stack

### Backend: Python Ecosystem
*   **Flask**: REST API orchestrator with CORS support
*   **MySQL**: Relational data persistence for movies, users, ratings, and watchlists
*   **Pandas/NumPy**: Heavy-duty data processing and vector math
*   **Scikit-learn**: Machine learning algorithms (TF-IDF, cosine similarity)
*   **SciPy**: SVD matrix factorization for collaborative filtering
*   **VADER Sentiment**: Emotion analysis for mood-based recommendations
*   **DeepFace + OpenCV**: Computer vision for emotion detection
*   **TensorFlow**: Neural network backend for DeepFace models

### Frontend: Modern Web Stack
*   **Next.js 16**: React framework with App Router
*   **React 19**: Component-based UI with hooks
*   **Tailwind CSS v4**: Utility-first styling with glassmorphism effects
*   **Vanilla JavaScript**: DOM manipulation and API integration

### Database Schema
*   **Movies Table**: id, title, genre, language, mood, rating, description, ott_platform, poster_url, release_year, cast_members
*   **Users Table**: id, username, password, preferences
*   **Watchlists Table**: user_id, movie_id relationships
*   **User Ratings Table**: user_id, movie_id, rating scores

---

## 🛠️ How to Test & Run

### Prerequisites
- **Python 3.8+** with pip (tested with Python 3.13)
- **Node.js 18+** with npm
- **MySQL Server** running locally
- **Webcam** (optional, for emotion detection feature)

### Installation & Setup

1. **Clone and Setup Environment**:
   ```bash
   git clone <repository-url>
   cd "Movie recommendation system"
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

2. **Install Backend Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Setup Database**:
   ```bash
   # Start MySQL server
   mysql -u root -p < database/schema.sql
   # Note: Update database credentials in backend/app.py if needed
   ```

4. **Train ML Models** (Optional but recommended):
   ```bash
   python train_models.py
   # This generates model_params.json with optimized hyperparameters
   ```

5. **Seed Database**:
   ```bash
   python init_db.py
   ```

6. **Install Frontend Dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start Backend**:
   ```bash
   cd backend
   python app.py
   # Runs on http://localhost:5000
   ```

2. **Start Frontend** (in new terminal):
   ```bash
   cd frontend
   npm run dev
   # Runs on http://localhost:3000
   ```

3. **Access Application**:
   - Open http://localhost:3000 in your browser
   - Register/Login to access the dashboard
   - Explore all 12 AI features through the sidebar tabs

### Testing Individual Features

- **Content-Based Recs**: Click any movie card to see "More Like This"
- **Collaborative Filtering**: Rate movies to get personalized recommendations
- **Mood Engine**: Use the "Mood Engine" tab to select emotions
- **NLP Search**: Try queries like "mind-bending thriller like Inception"
- **Trending**: Check "Trending" tab for live TMDB data
- **Diversity**: Explore "Discover" tab for MMR algorithm results
- **Profile Analytics**: Rate movies and check "My Profile" for insights
- **Emotion Detection**: Run `python backend/emotion_detection_page.py` separately

> [!TIP]
> **To test Emotion AI**: Run the standalone script `python backend/emotion_detection_page.py` and access the web interface it provides. Ensure you have good lighting for the DeepFace CNN to work effectively!

---

## 📊 Model Performance

The system includes automated model training and evaluation:
- **Training Script**: `backend/train_models.py`
- **Accuracy Report**: `backend/accuracy_report.json`
- **Model Parameters**: `backend/model_params.json`

Current performance metrics are tracked for all ML features with optimization suggestions.

---

## 🔧 Configuration

### Environment Variables
- **Backend**: Update database credentials in `backend/app.py`
- **TMDB API**: Add your API key to `backend/recommendation.py` for live trending data
- **DeepFace**: Models are downloaded automatically on first use

### Customization
- **Mood-Genre Mapping**: Modify `MOOD_GENRE_MAP` in `backend/recommendation.py`
- **Algorithm Weights**: Adjust hybrid scoring weights in recommendation functions
- **UI Themes**: Customize styles in `frontend/app/globals.css`

---

## 🤝 Contributing

1. **Model Training**: Run `python backend/train_models.py` after code changes
2. **Database**: Update `database/schema.sql` for schema changes
3. **Testing**: Test all 12 features manually through the UI
4. **Documentation**: Update this README and related docs

---

*Developed for Foundation Data Science (FDS) Project — Built with Python & React — 2026*#   M o v i e _ r e c o m m e n d a t i o n _ s y s t e m  
 