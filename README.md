# 🎬 CineIndia — AI-Powered Movie Recommendation System
### Foundation Data Science (FDS) Production Project

> **CineIndia** is a production-grade movie recommendation engine that leverages a multi-algorithm approach to solve the most difficult problems in information retrieval: the Cold Start problem, the Filter Bubble and lack of transparency (XAI).

📖 **[Project Navigation Guide](./PROJECT_DETAILS.md)** | ⚛️ **[Technical & Architecture Deep-Dive](./ABOUT_CINEINDIA.md)**

---

## 🏗️ Tech Stack

- **Backend**: Python, Flask, MySQL, Pandas/NumPy, Scikit-learn, SciPy, VADER, DeepFace, OpenCV
- **Frontend**: Next.js 16, React 19, Tailwind CSS v4

---

## 🛠️ Installation & Execution

### Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **MySQL Server**

### Steps
1. **Clone & Environment**:
   ```bash
   git clone <repository-url>
   cd "Movie recommendation system"
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. **Database Setup**: Start MySQL and import `database/schema.sql` (update credentials in `backend/app.py` if needed).

3. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python init_db.py  # Seed database
   python app.py      # Runs on port 5000
   ```

4. **Frontend Setup** (open a new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev        # Runs on port 3000
   ```

*For detailed insights on all 12 AI/ML algorithms, project logic, and system architecture, please see the [Technical & Architecture Deep-Dive](./ABOUT_CINEINDIA.md).*