# 🚦 Traffic Congestion Detection & Adaptive Signal Advisory System

An AI-powered traffic congestion detection and adaptive signal advisory system using
YOLOv8, OpenCV, object tracking, queue estimation, and FastAPI.

This system analyzes traffic video footage, estimates congestion per road approach
(N, S, E, W), detects choke points, and recommends optimal traffic signal green times.

---

## 📌 Key Features

- 🎥 Traffic video analysis using YOLOv8
- 🚗 Vehicle & pedestrian detection
- 🧭 ROI-based approach mapping (North, South, East, West)
- 🔁 Object tracking (Centroid + SORT/Kalman-based tracker)
- 📏 Queue length estimation (meters)
- 📊 Density-based congestion classification
- ⚠️ Choke point detection
- 🧠 Adaptive signal green-time advisory
- 🌐 FastAPI backend
- 💻 Frontend dashboard (HTML + JS)

---

## 🗂️ Project Structure

traffic_chatbot/
│
├── api/
│   └── main.py                  # FastAPI entry point
│
├── chatbot/
│   ├── traffic_advisor.py       # Advisory chatbot logic
│   ├── response_formatter.py
│
├── config/
│   ├── constants.py             # PCU values, limits, constants
│   ├── config.yaml
│
├── detector/
│   ├── object_detector.py       # YOLO detection wrapper
│   ├── object_tracker.py        # Simple centroid tracker
│   ├── sort_tracker.py          # Kalman-based SORT tracker
│   ├── queue_estimator.py       # Queue & congestion logic
│   ├── roi_config.py            # ROI polygon definitions
│   ├── roi_mapper.py            # Assign approach by point-in-polygon
│   ├── traffic_metrics.py       # TrafficMetrics dataclass
│   ├── metrics_builder.py       # Build metrics per approach
│   ├── visualize_roi.py         # YOLO + ROI + tracking visualization
│   ├── video_reader.py
│   ├── video_pipeline.py
│
├── engine/
│   ├── signal_optimizer.py      # Green time optimization
│   ├── rules.py
│   ├── traffic_math.py
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│
├── traffic.mp4                  # Sample input video
├── yolov8n.pt                   # YOLO model weights
├── requirements.txt
├── requirements_minimal.txt
├── README.md
└── .env

---

## ⚙️ System Requirements

- Python 3.9 – 3.11 (recommended: 3.10)
- Windows / Linux / macOS
- Optional: NVIDIA GPU (CUDA) for faster YOLO inference

---

## 📦 Installation

### 1️⃣ Clone the repository

git clone https://github.com/sabari-35/traffic_congestion_detector.git
cd traffic_chatbot

---

### 2️⃣ Create virtual environment

python -m venv venv

Activate it:

Windows:
venv\Scripts\activate

Linux / macOS:
source venv/bin/activate

---

### 3️⃣ Install dependencies

Minimal (API + logic only):

pip install -r requirements_minimal.txt

Full (YOLO + OpenCV + tracking):

pip install -r requirements.txt

---

### 4️⃣ YOLO Model

YOLOv8 weights (yolov8n.pt) are auto-downloaded by Ultralytics.
If needed:

pip install ultralytics

---

## ▶️ How to Run (Step-by-Step)

---

### 🔹 STEP 1: Test YOLO Detection

python -m detector.test_yolo

---

### 🔹 STEP 2: Test ROI Assignment

python -m detector.test_step1

---

### 🔹 STEP 3: Test Queue & Congestion Metrics

python -m detector.test_step3

---

### 🔹 STEP 4: Visualize YOLO + ROI + Tracking + Queue

python -m detector.test_step4

Controls:
- Press Q or ESC to exit
- Red boxes → queued vehicles
- Colored ROIs → approaches (N/S/E/W)

---

### 🔹 STEP 5: Run Signal Advisory Pipeline

python -m detector.test_step6

Sample output:

ChatbotResponse(
  recommended_green_times={'N': 15, 'S': 61.7, 'E': 22.7, 'W': 15},
  cycle_time=134.4,
  congestion levels,
  reasoning...
)

---

## 🌐 Run Backend API (FastAPI)

uvicorn api.main:app --reload

API URL:
http://127.0.0.1:8000

Endpoint:
POST /advise

---

## 💻 Run Frontend

Open directly in browser:
frontend/index.html

OR using VS Code Live Server:
http://127.0.0.1:5500/frontend/index.html

---

## 🚨 Core Concepts Explained

### 🚗 Queue Length
Estimated using:
queue_length = vehicle_count × 5.5 meters

---

### 📊 Density
density = PCU / number_of_lanes

---

### 🚦 Congestion Levels

free                → low queue + low density  
stable              → moderate traffic  
congested           → high queue or density  
severely_congested  → extreme queue / density  

---

### ⚠️ Choke Point (IMPORTANT)

A choke point is detected when:
- Vehicle count remains high
- Vehicles move very slowly
- Condition persists for many frames

Your OLD code ❌:
- Did NOT detect choke points
- Used only instant vehicle count

Your NEW code ✅:
- Uses tracking + time persistence
- Detects real choke points reliably

---

## 🧠 Why This Architecture Works Well

- Modular (Detection → Metrics → Advisory)
- Replaceable tracker (Centroid ↔ SORT)
- Scales to live CCTV feeds
- Real traffic-engineering logic
- API + UI ready
- Easy to extend (emergency priority, DB, ML)

---

## 🚀 Future Enhancements

- Emergency vehicle prioritization
- Multi-camera fusion
- Database logging
- WebSocket live updates
- Real traffic controller integration

---



