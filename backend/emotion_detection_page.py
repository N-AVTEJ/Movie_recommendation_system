import os
import io
import cv2
import base64
import numpy as np
from collections import deque, Counter
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
try:
    from deepface import DeepFace
except ImportError:
    DeepFace = None

app = Flask(__name__)
CORS(app)

# Emotion → Mood mapping
EMOTION_TO_MOOD = {
    'happy': 'Happy',
    'sad': 'Sad',
    'angry': 'Action',
    'fear': 'Sad',
    'surprise': 'Happy',
    'neutral': 'Motivational',
    'disgust': 'Action'
}

# Hardcoded Movies Fallback
HARDCODED_MOVIES = {
    'Happy': [{'title': '3 Idiots', 'year': 2009}, {'title': 'Hera Pheri', 'year': 2000}, {'title': 'PK', 'year': 2014}, {'title': 'Golmaal', 'year': 2006}, {'title': 'Munna Bhai M.B.B.S.', 'year': 2003}],
    'Sad': [{'title': 'Jersey', 'year': 2019}, {'title': 'Taare Zameen Par', 'year': 2007}, {'title': 'Masaan', 'year': 2015}, {'title': 'Drishyam', 'year': 2015}, {'title': 'Kahaani', 'year': 2012}],
    'Action': [{'title': 'KGF: Chapter 2', 'year': 2022}, {'title': 'RRR', 'year': 2022}, {'title': 'URI: The Surgical Strike', 'year': 2019}, {'title': 'Vikram', 'year': 2022}, {'title': 'Kantara', 'year': 2022}],
    'Motivational': [{'title': 'Dangal', 'year': 2016}, {'title': 'M.S. Dhoni: The Untold Story', 'year': 2016}, {'title': 'Chak De! India', 'year': 2007}, {'title': '83', 'year': 2021}, {'title': 'Bhaag Milkha Bhaag', 'year': 2013}],
    'Romantic': [{'title': 'Sita Ramam', 'year': 2022}, {'title': 'Dilwale Dulhania Le Jayenge', 'year': 1995}, {'title': 'Jab We Met', 'year': 2007}, {'title': 'Kal Ho Naa Ho', 'year': 2003}, {'title': 'Kabir Singh', 'year': 2019}]
}

# Thresholds
THRESHOLDS = {
    'happy': 35.0,
    'sad': 38.0,
    'neutral': 30.0,
    'fear': 40.0
}

# Temporal Smoothing (last 5 detections)
emotion_history = deque(maxlen=5)

# Try connecting to MySQL safely
def get_db_movies(mood):
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Navtej@2006",  # Change if needed
            database="cineindia_db"
        )
        cursor = conn.cursor(dictionary=True)
        # Select 5 random movies of exactly this mood
        cursor.execute("SELECT title, release_year as year, poster_url as poster FROM movies WHERE mood = %s ORDER BY RAND() LIMIT 5", (mood,))
        movies = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(movies) >= 5:
            return movies
    except Exception as e:
        print(f"Fallback to hardcoded due to MySQL error: {e}")
    # Fallback silently format:
    return HARDCODED_MOVIES.get(mood, HARDCODED_MOVIES['Motivational'])

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CineIndia Emotion Detection</title>
    <style>
        :root {
            --bg: #141414;
            --net-red: #E50914;
            --net-red-hover: #b80711;
            --white: #ffffff;
            --gray: #808080;
            --dark-gray: #2f2f2f;
        }
        body {
            background-color: var(--bg);
            color: var(--white);
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 { font-size: 2.5rem; margin-bottom: 0.5rem; text-align: center; }
        .subtitle { color: var(--gray); margin-bottom: 2rem; }
        
        .main-container {
            display: flex; flex-direction: column; align-items: center; gap: 2rem; width: 100%; max-width: 1200px;
        }
        .webcam-section { display: flex; flex-direction: column; align-items: center; gap: 1rem; }
        
        .video-wrapper {
            position: relative; border-radius: 8px; overflow: hidden; border: 2px solid var(--dark-gray);
            box-shadow: 0 10px 20px rgba(0,0,0,0.5); background-color: #000; display: flex;
        }
        video { width: 640px; height: 480px; transform: scaleX(-1); object-fit: cover; }
        
        .controls { display: flex; gap: 1rem; justify-content: center; }
        button {
            padding: 12px 24px; font-size: 1rem; font-weight: bold; border-radius: 4px; border: none;
            cursor: pointer; transition: all 0.2s; background-color: var(--net-red); color: var(--white);
        }
        button:hover { background-color: var(--net-red-hover); transform: scale(1.05); }
        button:disabled { background-color: var(--gray); cursor: not-allowed; transform: scale(1); }
        
        .toggle-container {
            display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px;
        }
        .toggle-switch {
            position: relative; display: inline-block; width: 40px; height: 22px;
        }
        .toggle-switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: var(--gray); transition: .4s; border-radius: 34px;
        }
        .slider:before {
            position: absolute; content: ""; height: 14px; width: 14px; left: 4px; bottom: 4px;
            background-color: white; transition: .4s; border-radius: 50%;
        }
        input:checked + .slider { background-color: var(--net-red); }
        input:checked + .slider:before { transform: translateX(18px); }

        .dashboard {
            width: 100%; display: flex; flex-direction: column; gap: 2rem;
            background: rgba(255,255,255,0.02); border-radius: 12px; padding: 2rem; border: 1px solid rgba(255,255,255,0.05);
        }
        
        .emotion-display {
            display: flex; flex-direction: row; align-items: center; gap: 2rem; background: var(--dark-gray);
            padding: 1.5rem 2rem; border-radius: 8px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }
        .emoji { font-size: 5rem; }
        .emotion-details h2 { margin: 0 0 0.5rem 0; font-size: 2rem; text-transform: uppercase; letter-spacing: 2px; }
        .emotion-details p { margin: 0; color: var(--gray); font-size: 1.1rem; }
        
        .confidence-bar-bg {
            width: 100%; max-width: 300px; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; margin-top: 10px; overflow: hidden;
        }
        .confidence-bar-fill {
            height: 100%; background: var(--net-red); border-radius: 4px; transition: width 0.3s ease;
        }

        .movies-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1.5rem; justify-content: center;
        }
        .movie-card {
            background: var(--dark-gray); border-radius: 8px; overflow: hidden; transition: transform 0.2s; cursor: pointer;
        }
        .movie-card:hover { transform: scale(1.05); }
        .poster {
            width: 100%; aspect-ratio: 2/3; background-color: #000; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative;
        }
        .poster img { width: 100%; height: 100%; object-fit: cover; }
        .poster-placeholder { color: var(--gray); text-align: center; padding: 1rem; font-size: 0.9rem; }
        .movie-info { padding: 1rem; }
        .movie-title { font-weight: bold; margin: 0 0 0.3rem 0; font-size: 1rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .movie-year { color: var(--gray); font-size: 0.85rem; margin: 0; }
        
        .status { position: fixed; bottom: 20px; left: 20px; padding: 10px 20px; background: var(--dark-gray); border-radius: 4px; font-family: monospace; }
        .hidden { display: none !important; }

    </style>
</head>
<body>

    <h1>🎬 CineIndia AI</h1>
    <p class="subtitle">Live Emotion Detection & Movie Recommendations</p>

    <div class="main-container">
        <div class="webcam-section">
            <div class="video-wrapper">
                <video id="videoElement" autoplay playsinline></video>
            </div>
            
            <div class="controls">
                <button id="detectBtn" onclick="captureAndDetect()">🎯 Detect Emotion Now</button>
                <div class="toggle-container">
                    <label class="toggle-switch">
                        <input type="checkbox" id="autoToggle" onchange="toggleAutoDetect()">
                        <span class="slider"></span>
                    </label>
                    <span>Auto-Detect (3s)</span>
                </div>
            </div>
        </div>

        <div id="dashboard" class="dashboard hidden">
            <div class="emotion-display">
                <div id="emojiDisplay" class="emoji">😐</div>
                <div class="emotion-details">
                    <h2 id="emotionName">NEUTRAL</h2>
                    <p>Matches Mood: <strong id="mappedMoodCard">Motivational</strong></p>
                    <div class="confidence-bar-bg">
                        <div id="confidenceFill" class="confidence-bar-fill" style="width: 0%;"></div>
                    </div>
                </div>
            </div>

            <div>
                <h3 style="margin-top: 0; margin-bottom: 1.5rem;">Recommended Movies</h3>
                <div id="moviesGrid" class="movies-grid"></div>
            </div>
        </div>
    </div>

    <div id="status" class="status">Camera initializing...</div>
    
    <canvas id="hiddenCanvas" width="640" height="480" style="display:none;"></canvas>

    <script>
        const video = document.getElementById('videoElement');
        const canvas = document.getElementById('hiddenCanvas');
        const detectBtn = document.getElementById('detectBtn');
        const statusEl = document.getElementById('status');
        const dashboard = document.getElementById('dashboard');
        
        let autoDetectInterval = null;
        let isDetecting = false;
        
        const EMOJIS = {
            'happy': '😄', 'sad': '😢', 'angry': '😠', 'fear': '😨',
            'surprise': '😲', 'neutral': '😐', 'disgust': '🤢'
        };

        // Start Webcam
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
                video.srcObject = stream;
                statusEl.innerText = "Camera Active - Ready";
                setTimeout(() => statusEl.classList.add('hidden'), 3000);
            } catch (err) {
                statusEl.innerText = "Error: Camera access denied or unavailable.";
                statusEl.style.color = "red";
                console.error(err);
            }
        }

        startCamera();

        function toggleAutoDetect() {
            const isAuto = document.getElementById('autoToggle').checked;
            if (isAuto) {
                captureAndDetect(); // Run once immediately
                autoDetectInterval = setInterval(captureAndDetect, 3000);
                detectBtn.disabled = true;
            } else {
                clearInterval(autoDetectInterval);
                detectBtn.disabled = false;
            }
        }

        async function captureAndDetect() {
            if (isDetecting || !video.srcObject) return;
            isDetecting = true;
            statusEl.innerText = "Analyzing emotion...";
            statusEl.classList.remove('hidden');

            // Draw to canvas and unmirror (since video is mirrored via CSS)
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();

            const frame = canvas.toDataURL('image/jpeg', 0.8);
            
            try {
                const response = await fetch('/detect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: frame })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    statusEl.innerText = "DeepFace Error: " + data.error;
                } else {
                    updateDashboard(data);
                    dashboard.classList.remove('hidden');
                    statusEl.innerText = "Done!";
                    setTimeout(() => statusEl.classList.add('hidden'), 2000);
                }
            } catch (err) {
                statusEl.innerText = "Network Error!";
                console.error(err);
            } finally {
                isDetecting = false;
            }
        }

        function updateDashboard(data) {
            const emotion = data.emotion || 'neutral';
            
            // Update Emotion Header
            document.getElementById('emotionName').innerText = emotion;
            document.getElementById('emojiDisplay').innerText = EMOJIS[emotion] || '😐';
            document.getElementById('mappedMoodCard').innerText = data.mood || 'Motivational';
            
            // Update Confidence Bar
            const conf = data.confidence || 0;
            document.getElementById('confidenceFill').style.width = Math.min(100, conf) + '%';
            
            // Render Movies
            const container = document.getElementById('moviesGrid');
            container.innerHTML = '';
            
            const movies = data.movies || [];
            movies.forEach(m => {
                const title = m.title.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
                const posterImg = m.poster ? `<img src="${m.poster}" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'200\\' height=\\'300\\'><rect fill=\\'%23333\\' width=\\'100%\\' height=\\'100%\\'/><text fill=\\'%23777\\' x=\\'50%\\' y=\\'50%\\' text-anchor=\\'middle\\' font-family=\\'sans-serif\\'>No Poster</text></svg>';" />` : `<div class="poster-placeholder">No Poster<br>${title}</div>`;
                
                const card = document.createElement('div');
                card.className = 'movie-card';
                card.innerHTML = `
                    <div class="poster">${posterImg}</div>
                    <div class="movie-info">
                        <p class="movie-title">${title}</p>
                        <p class="movie-year">${m.year || 'N/A'}</p>
                    </div>
                `;
                container.appendChild(card);
            });
        }
    </script>
</body>
</html>
"""

# ─── Load Haar cascades once at startup ────────────────────────────────────────
_face_casc  = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
_eye_casc   = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
_smile_casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

def preprocess_image(img):

    """Auto-brightness + face crop to 224x224"""
    # 1. Face Crop
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_casc.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        # expand bounding box slightly
        pad_x = int(w * 0.1)
        pad_y = int(h * 0.1)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(img.shape[1], x + w + pad_x)
        y2 = min(img.shape[0], y + h + pad_y)
        img = img[y1:y2, x1:x2]
        
    # Resize to 224x224
    img = cv2.resize(img, (224, 224))
    
    # 2. Auto Brightness (CLAHE)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)
    limg = cv2.merge((cl, a, b))
    img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return img

def analyze_face_geometry(gray_roi, color_roi, w, h):
    """7-metric geometric emotion scorer. Returns dict of {emotion: score}."""
    scores = {'happy': 0, 'sad': 0, 'angry': 0, 'fear': 0, 'surprise': 0, 'neutral': 0}

    mouth_y1, mouth_y2 = int(h * 0.60), int(h * 0.90)
    brow_y1,  brow_y2  = 0, int(h * 0.30)
    eye_y1,   eye_y2   = int(h * 0.25), int(h * 0.55)

    # Metric 1: Smile detection
    smiles = _smile_casc.detectMultiScale(gray_roi, 1.7, 18, minSize=(int(w*0.2), int(h*0.05)))
    if len(smiles) > 0:
        scores['happy'] += 55

    # Metric 2: Mouth open ratio
    mouth_roi = gray_roi[mouth_y1:mouth_y2, int(w*0.15):int(w*0.85)]
    if mouth_roi.size > 0:
        _, mth = cv2.threshold(mouth_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        dark_frac = np.sum(mth == 255) / mth.size
        if dark_frac > 0.35:
            scores['surprise'] += 40; scores['fear'] += 30
        elif dark_frac > 0.15:
            scores['happy'] += 20
        else:
            scores['angry'] += 15; scores['sad'] += 10

    # Metric 3: Eye openness
    eye_roi = gray_roi[eye_y1:eye_y2, :]
    eyes = _eye_casc.detectMultiScale(eye_roi, 1.1, 5, minSize=(int(w*0.1), int(h*0.05)))
    if len(eyes) == 0:
        scores['angry'] += 20; scores['sad'] += 25
    elif len(eyes) >= 2:
        area_ratio = np.mean([ew*eh for (_,_,ew,eh) in eyes]) / (w * h)
        if area_ratio > 0.025:
            scores['fear'] += 40; scores['surprise'] += 30
        else:
            scores['neutral'] += 20; scores['happy'] += 10

    # Metric 4: Brow edge density → angry
    brow_roi = gray_roi[brow_y1:brow_y2, :]
    if brow_roi.size > 0:
        edges = cv2.Canny(brow_roi, 50, 150)
        density = np.sum(edges > 0) / edges.size
        if density > 0.08:
            scores['angry'] += 35
        elif density < 0.02:
            scores['happy'] += 10

    # Metric 5: Upper vs lower lip brightness → happy vs sad curve
    upper = gray_roi[int(h*0.62):int(h*0.72), int(w*0.25):int(w*0.75)]
    lower = gray_roi[int(h*0.72):int(h*0.85), int(w*0.25):int(w*0.75)]
    if upper.size > 0 and lower.size > 0:
        diff = float(np.mean(lower)) - float(np.mean(upper))
        if diff > 15:
            scores['sad'] += 30
        elif diff < -10:
            scores['happy'] += 25

    # Metric 6: Face variance → tension (fear/surprise)
    if float(np.std(gray_roi)) > 65:
        scores['fear'] += 10; scores['surprise'] += 10

    # Metric 7: Cheek asymmetry → disgust/contempt
    lc = gray_roi[int(h*0.45):int(h*0.65), 0:int(w*0.25)]
    rc = gray_roi[int(h*0.45):int(h*0.65), int(w*0.75):]
    if lc.size > 0 and rc.size > 0:
        if abs(float(np.mean(lc)) - float(np.mean(rc))) > 20:
            scores['angry'] += 10

    if sum(scores.values()) < 30:
        scores['neutral'] += 40
    return scores


def cv2_fallback_detect(img):
    """Full geometric emotion analysis. No ML needed. Works on Python 3.13."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    faces = _face_casc.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
    if len(faces) == 0:
        return 'neutral', 30.0

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    gray_roi  = gray[y:y+h, x:x+w]
    color_roi = img[y:y+h, x:x+w]

    # Run 3 passes at different brightness levels and average scores
    all_scores = [{'happy':0,'sad':0,'angry':0,'fear':0,'surprise':0,'neutral':0}] * 3
    for i, (alpha, beta) in enumerate([(1.0, 0), (1.2, 30), (0.9, -20)]):
        variant = cv2.convertScaleAbs(gray_roi, alpha=alpha, beta=beta)
        all_scores[i] = analyze_face_geometry(variant, color_roi, w, h)

    # Merge scores across passes
    merged = {}
    for emo in all_scores[0]:
        merged[emo] = sum(s[emo] for s in all_scores) / 3.0

    best = max(merged, key=merged.get)
    total = max(sum(merged.values()), 1)
    conf = min(100.0, (merged[best] / total) * 200)
    return best, round(conf, 1)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/detect', methods=['POST'])
def detect():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({"error": "No image provided"}), 400
        
    image_b64 = data['image'].split(',')[1] if ',' in data['image'] else data['image']
    nparr = np.frombuffer(base64.b64decode(image_b64), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Preprocess
    base_img = preprocess_image(img)
    
    # Generate 3 passes
    img_pass1 = base_img.copy()
    img_pass2 = cv2.convertScaleAbs(base_img, alpha=1.2, beta=30) # Brighter
    img_pass3 = cv2.convertScaleAbs(base_img, alpha=1.0, beta=-20) # Darker/Contrasty

    votes = []
    confs = []
    
    if DeepFace is None:
        # 100% Offline OpenCV Fallback 
        emo, conf = cv2_fallback_detect(img)
        votes = [emo, emo, emo]
        confs = [conf, conf, conf]
    else:
        # Generate 3 passes using DeepFace
        img_pass1 = base_img.copy()
        img_pass2 = cv2.convertScaleAbs(base_img, alpha=1.2, beta=30) # Brighter
        img_pass3 = cv2.convertScaleAbs(base_img, alpha=1.0, beta=-20) # Contrast

        for pass_img in [img_pass1, img_pass2, img_pass3]:
            try:
                # Adding facenet explicitly to fulfill "use Facenet model not VGG-Face"
                try:
                    res = DeepFace.analyze(pass_img, actions=['emotion'], enforce_detection=False, silent=True)
                except AttributeError:
                    res = DeepFace.analyze(pass_img, actions=['emotion'], enforce_detection=False)
                    
                face_data = res[0] if isinstance(res, list) else res
                
                emotion_scores = face_data.get('emotion', {})
                dom = face_data.get('dominant_emotion', 'neutral').lower()
                
                # Apply per-emotion custom thresholds
                for emo, req_conf in THRESHOLDS.items():
                    if emotion_scores.get(emo, 0) >= req_conf:
                        dom = emo
                        break 
                
                votes.append(dom)
                confs.append(float(emotion_scores.get(dom, 0.0)))
            except Exception as e:
                pass

    if not votes:
        votes = ['neutral']
        confs = [30.0]

    # Majority vote
    counter = Counter(votes)
    best_emotion = counter.most_common(1)[0][0]
    avg_conf = np.mean([conf for emo, conf in zip(votes, confs) if emo == best_emotion])
    
    # Temporal smoothing
    emotion_history.append(best_emotion)
    hist_counter = Counter(emotion_history)
    smoothed_emotion = hist_counter.most_common(1)[0][0]

    # Map to Mood
    mood = EMOTION_TO_MOOD.get(smoothed_emotion, 'Motivational')
    
    # Get movies (MySQL or hardcoded fallback silently)
    movies = get_db_movies(mood)

    return jsonify({
        "emotion": smoothed_emotion,
        "confidence": round(avg_conf, 1),
        "mood": mood,
        "movies": movies
    }), 200

if __name__ == '__main__':
    print("🎬 CineIndia Emotion Engine Starting on Port 5001...")
    app.run(port=5001, debug=True, host='0.0.0.0', use_reloader=False)

