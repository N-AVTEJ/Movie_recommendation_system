# 🕵️ CineIndia — Project Deep-Dive & Architecture Guide

This guide provides an academic-level explanation of the **CineIndia** system architecture, the libraries used for each feature, and the mathematical logic behind the recommendations.

---

## 🏗️ Technical Architecture Overview
CineIndia is built as a **Decoupled Monolith**.
1.  **Frontend (Next.js 16 + React 19)**: Handles UI, State (React Hooks), and Browser APIs.
2.  **Backend (Flask + MySQL)**: The "Brain" of the system. It processes ML requests, interacts with the MySQL database, and handles external API calls (TMDB).
3.  **Database (MySQL)**: Persistent storage for movie metadata, user ratings, and watchlists.

---

## 🔬 Feature-to-Library Mapping

### 1. The Core AI: Content-Based Filtering
*   **Feature**: Finding similarity between movies.
*   **Library**: `scikit-learn` (`TfidfVectorizer`, `cosine_similarity`)
*   **Explanation**: We convert text (genres + cast + description) into a numerical matrix. Each movie becomes a vector. We calculate the **Cosine** of the angle between vectors. A smaller angle (value closer to 1.0) means the movies are highly similar.

### 2. Social Wisdom: Collaborative Filtering
*   **Feature**: User-to-User similarity.
*   **Library**: `scipy` (`svds`)
*   **Explanation**: We use **Matrix Factorization (SVD)**. If User A and User B both liked Movie X, and User A liked Movie Y, the system predicts User B will also like Movie Y. SVD handles the sparsity of the rating matrix to make these predictions stable.

### 3. The Emotional AI: Mood & Sentiment
*   **Feature**: Mood-based recommendations.
*   **Library**: `vaderSentiment` (`SentimentIntensityAnalyzer`)
*   **Explanation**: We don't just use genres. We use **NLP Sentiment Analysis** on the plot summary. For a "Happy" mood, we boost movies that have a positive sentiment score (> 0.5) and penalize those with negative scores.

### 4. Facial Recognition: Emotion Detection
*   **Feature**: Real-time webcam suggestions.
*   **Library**: `deepface`, `opencv-python`
*   **Explanation**: We utilize a **Pre-trained Deep Neural Network (CNN)**. It analyzes facial landmarks and pixel intensity to classify your facial expression into 7 categories. We use the `opencv` backend for faster frame processing during the detection phase.
*   **Note**: Currently implemented as standalone script (`emotion_detection_page.py`).

### 5. Smart Search: Natural Language NLP
*   **Feature**: Conversational search.
*   **Library**: `scikit-learn`, `vaderSentiment`
*   **Explanation**: Instead of matching exact strings, we vectorize your query. *"I want something dark but exciting"* is translated into mathematical weights for "Thriller" and "Action" while checking for high-intensity descriptions.

### 6. Transparency: Explainable AI (XAI)
*   **Feature**: Recommendation explanations.
*   **Engine**: Custom NLP Logic.
*   **Explanation**: The system compares the TF-IDF features of your favorite movie and the recommendation. If the "Action" feature and "Ram Charan" feature are the strongest overlaps, it generates a human sentence: *"Because you liked RRR, this film was recommended — it shares the Action genre and features Ram Charan."*

### 7. Global Data: Real-Time Trending
*   **Feature**: Live cinema data.
*   **Library**: `requests`
*   **Explanation**: We make RESTful calls to the **TMDB (TheMovieDB) API**. This provides real-time information on what is currently popular worldwide, which we then merge with our local data.

---

## 📈 Mathematics of Diversity (MMR)
We use **Maximal Marginal Relevance (MMR)** to prevent "Filter Bubbles."
**The Equation:** `MMR = λ * Similarity - (1 - λ) * Diversity`
By setting `λ = 0.5`, we ensure that the top choices are not just the most similar, but are also different enough from each other to keep the user's feed interesting.

---

## 🎬 How each feature solves a problem:
*   **Cold Start**: Solved by the **Onboarding Quiz**.
*   **Discovery**: Solved by **Hybrid AI** (weighted blend).
*   **Engagement**: Solved by **Netflix-Style UI** and **Emotion AI**.
*   **Trust**: Solved by **Explainable AI (XAI)**.

---
*CineIndia: Foundation Data Science — Built with Python & React*

