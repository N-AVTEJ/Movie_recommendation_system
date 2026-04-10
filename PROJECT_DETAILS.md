# 🎬 CineIndia — Project Explanation & Feature Guide

This document provides a detailed breakdown of all core **AI/ML features** and **future enhancements** in the CineIndia Movie Recommendation System, along with instructions on how to test them.

---

## 🚀 Core AI Features (Live Now)

These features are fully integrated into the CineIndia dashboard.

### 1. Content-Based Filtering (TF-IDF)
*   **What it is**: Recommends movies similar to one you already like.
*   **How it works**: It tokenizes the `genre`, `description`, `cast`, and `mood` of every movie. It then builds a **TF-IDF Matrix** and uses **Cosine Similarity** to find the "closest" matches in the vector space.
*   **Test by**: Clicking on any movie card (e.g., "RRR") and looking at the "More Like This" section.

### 2. Collaborative Filtering (SVD)
*   **What it is**: "Users who liked this also liked..."
*   **How it works**: It uses **Singular Value Decomposition (SVD)** on the user-movie rating matrix. It identifies patterns in how different users rate movies to predict what you might like even if you haven't seen it yet.
*   **Requirement**: You need to rate a few movies first so the AI can understand your taste.

### 3. Hybrid Recommendation
*   **What it is**: The best of both worlds.
*   **How it works**: It calculates a weighted score: **60% Content-based + 40% Collaborative**. This ensures you get movies that are similar to your favorites but also surprising recommendations from other users.

### 4. Mood-Based Recommendation
*   **What it is**: Matches your current feeling to a movie genre.
*   **How it works**: Uses a mapping (e.g., Happy → Comedy) combined with **VADER Sentiment Analysis** on movie descriptions to ensure the *tone* of the movie matches your mood.

---

## 🔮 Roadmap: Future Enhancements

The following features represent the "Phase 2" of CineIndia development. We focus on automated intelligence and cutting-edge vision AI.

### 🌟 Vision AI: Real-time Emotion Detection
**Status**: Experimental Standalone Prototype Ready.

**Note**: The emotion detection feature is planned as a future enhancement and is currently available only as an experimental standalone script. It is designed to eventually replace manual mood selection with automated facial analysis.

### How to Test the Emotion AI Prototype (Step-by-Step)

If you want to test the webcam-based recommendation feature:

1.  **Run the Standalone Script**:
    ```bash
    cd backend
    python emotion_detection_page.py
    ```

2.  **Access the Web Interface**:
    - The script will start a local web server
    - Open the provided URL in your browser (typically http://localhost:5001 or similar)

3.  **Grant Permissions**: If your browser asks for camera access, click **Allow**.

4.  **Start Camera**: Click the red **"Start Camera"** button. You should see your live video feed appear on the screen.

5.  **Pose**: Look directly at the camera. Try to express a specific emotion (Smile for Happy, Frown for Sad, or keep a blank face for Neutral).

6.  **Detect Emotion**: Click the **"Detect My Emotion"** button.
    *   The system will capture a frame and send it to the backend.
    *   **Backend Logic**: It uses `DeepFace` (with `opencv` backend) to analyze your facial expression.
    *   **Confidence**: It only accepts results with >40% confidence.

7.  **Results**: You will see your detected emotion (e.g., "HAPPY") and a list of movies matched to that mood (e.g., 3 Idiots, Hera Pheri).

---

## 🧠 Deep-Dive: Other Core Capabilities

### 6. Explainable AI (XAI)
*   **What it is**: No more "Black Box" recommendations.
*   **How it works**: When the AI recommends a movie, it generates a human-readable reason (e.g., *"Because you liked RRR, this film was recommended — it shares the Action genre and matches the Motivational mood."*).

### 7. Natural Language Search (NLP)
*   **What it is**: Search like you're talking to a friend.
*   **How it works**: Type queries like *"mind-bending movies like Inception"* or *"I want something sad but inspiring"*. The system uses TF-IDF and sentiment analysis to understand your *intent* rather than just keywords.

### 8. Real-Time Trending (TMDB)
*   **What it is**: What the world is watching right now.
*   **How it works**: Connects to the **TheMovieDB (TMDB) API** to fetch live trending data. If the API is down, it falls back to the top-rated movies in our local database.

### 9. Cold Start Solution (Onboarding Quiz)
*   **What it is**: Fixes the problem where new users have no recommendations.
*   **How it works**: During login, users take a quick quiz. The AI uses these preferences to build an "Instant Profile" and provide immediate recommendations.

### 10. Diversity-Aware Recommendations (MMR)
*   **What it is**: Avoids "Filter Bubbles" (seeing the same types of movies).
*   **How it works**: Uses **Maximal Marginal Relevance (MMR)**. It doesn't just pick the most similar movies; it picks movies that are similar to your taste *but different from each other*.

### 11. User Profile Dashboard
*   **What it is**: A visual summary of your "Movie DNA".
*   **How it works**: Aggregates your ratings and watchlist into charts (Genre distribution, Yearly trends) so you can see how your taste is evolving.

### 12. Netflix-Style Premium UI
*   **What it is**: High-end user experience.
*   **How it works**: Features **Glassmorphism**, smooth animations, YouTube trailer embeds, and OTT badges (Netflix, Prime, etc.) to make the system feel like a production-grade app.

---

## 🛠️ Developer Notes: Troubleshooting Images
If an image fails to load (e.g., a Wikipedia link is blocked), the frontend automatically falls back to a high-quality movie theater placeholder image to ensure the UI stays beautiful.
