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
*   **Library**: `Next.js`, `Charts.js (logic-ready)`
*   **Logic**: Aggregates all user interactions (ratings, watchlist) and calculates distribution percentages.
*   **Feature Goal**: Visualizing your movie evolution and most-watched genres.

### 12. Netflix-Style Glassmorphism UI
*   **Tech**: `Next.js 16`, `Vanilla CSS`
*   **Logic**: High-end UX design featuring dark mode, glassmorphism, smooth animations, and interactive trailer overlays via YouTube/TMDB.
*   **Feature Goal**: Providing a commercial-grade, "Wow" factor interface.

---

## 🏗️ Architecture & Tech Stack

### Backend: Python Ecosystem
*   **Flask**: REST API orchestrator.
*   **MySQL**: Relational data persistence for 45+ movies, users, and ratings.
*   **Pandas/NumPy**: Heavy-duty data processing and vector math.

### Frontend: Modern Web
*   **Next.js (React)**: Component-based architecture with client-side state management.
*   **Webcam API**: Direct browser access for the Vision AI module.

---

## 🛠️ How to Test & Run

1.  **Database**: Run `python backend/init_db.py` to seed the complex movie library.
2.  **Backend**: `cd backend && python app.py` (Runs on Port 5000).
3.  **Frontend**: `cd frontend && npm run dev` (Runs on Port 3000).

> [!TIP]
> **To test Emotion AI**: Go to the **Emotion AI** tab, click **Start Camera**, and use **Detect Emotion**. Ensure you have good lighting for the DeepFace CNN to work effectively!

---
*Developed for Foundation Data Science (FDS) Project — 2026*


python emotion_detection_page.py
