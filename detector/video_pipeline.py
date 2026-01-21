from typing import List, Dict
from detector.traffic_metrics import TrafficMetrics
from detector.object_detector import ObjectDetector
from detector.object_tracker import ObjectTracker
from detector.queue_estimator import QueueEstimator
from detector.video_reader import VideoReader
from detector.roi_mapper import assign_approach
from config.constants import TrafficConstants

# ==============================
# CONSTANTS
# ==============================
VEHICLE_LENGTH_M = 5.5  # avg vehicle + gap (meters)
LANES = {"N": 3, "S": 3, "E": 2, "W": 1}

# ==============================
# INIT (SINGLETONS)
# ==============================
tracker = ObjectTracker()
queue_estimator = QueueEstimator()

# ==============================
# QUEUE + CONGESTION HELPERS
# ==============================
def estimate_queue_length(vehicle_counts: Dict[str, float]) -> float:
    total_vehicles = sum(vehicle_counts.values())
    return round(total_vehicles * VEHICLE_LENGTH_M, 1)


def classify_congestion(queue_length: float, density: float) -> str:
    if queue_length > 120 or density > 80:
        return "severely_congested"
    elif queue_length > 80 or density > 50:
        return "congested"
    elif queue_length > 40 or density > 25:
        return "stable"
    return "free"


# ==============================
# STEP 1: VIDEO → TRACKED OBJECTS
# ==============================
def extract_tracked_objects(video_path: str, max_frames: int = 300):
    reader = VideoReader(video_path)
    detector = ObjectDetector()

    tracked_objects = []
    frame_count = 0

    while True:
        frame = reader.read()
        if frame is None or frame_count >= max_frames:
            break

        detections = detector.detect(frame)

        formatted = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            formatted.append({
                "bbox": (x1, y1, x2, y2),
                "center": (cx, cy),
                "label": det["label"]
            })

        # TRACK
        tracked = tracker.update(formatted)

        # QUEUE
        queue_objs = queue_estimator.update(tracked)
        queue_ids = {q["id"] for q in queue_objs}

        # ASSIGN APPROACH *AFTER* TRACKING
        for obj in tracked:
            cx, cy = obj["center"]
            approach = assign_approach(cx, cy)

            if approach is None:
                continue

            tracked_objects.append({
                "label": obj["label"],
                "approach": approach,        # NOW CORRECT
                "is_queued": obj["id"] in queue_ids
            })

        frame_count += 1

    reader.release()
    return tracked_objects


# ==============================
# STEP 2–3: BUILD METRICS
# ==============================
def build_metrics(tracked_objects: List[Dict]) -> Dict[str, TrafficMetrics]:
    metrics = {}

    for approach in ["N", "S", "E", "W"]:
        vehicle_counts: Dict[str, float] = {}
        pedestrians = 0

        for obj in tracked_objects:
            if obj["approach"] != approach:
                continue

            if obj["label"] == "person":
                pedestrians += 1
            else:
                # 🚦 HYBRID CONTRIBUTION
                weight = 1.0 if obj.get("is_queued") else 0.3
                vehicle_counts[obj["label"]] = (
                    vehicle_counts.get(obj["label"], 0) + weight
                )

        queue_length = estimate_queue_length(vehicle_counts)

        temp = TrafficMetrics(
            approach_id=approach,
            vehicle_counts=vehicle_counts,
            queue_length=queue_length,
            lanes=LANES[approach],
            congestion_level="free",
            pedestrian_count=pedestrians,
            current_green_time=30
        )

        density = temp.demand_pcu / max(LANES[approach], 1)
        congestion = classify_congestion(queue_length, density)

        metrics[approach] = TrafficMetrics(
            approach_id=approach,
            vehicle_counts=vehicle_counts,
            queue_length=queue_length,
            lanes=LANES[approach],
            congestion_level=congestion,
            pedestrian_count=pedestrians,
            current_green_time=30
        )

    return metrics


# ==============================
# STEP 4: API FORMAT
# ==============================
def build_traffic_data(metrics: Dict[str, TrafficMetrics]) -> Dict:
    return {
        "approaches": [
            {
                "approach_id": m.approach_id,
                "vehicle_counts": m.vehicle_counts,
                "queue_length": m.queue_length,
                "lanes": m.lanes,
                "congestion_level": m.congestion_level,
                "pedestrian_count": m.pedestrian_count,
                "current_green_time": m.current_green_time
            }
            for m in metrics.values()
        ],
        "current_cycle_time": TrafficConstants.DEFAULT_CYCLE_TIME,
        "emergency_vehicle_present": False,
        "format": "json"
    }


# ==============================
# SINGLE-CAMERA WRAPPER
# ==============================
def run_video_pipeline(video_path: str, approach: str):
    tracked = extract_tracked_objects(video_path, max_frames=300)
    metrics = build_metrics(tracked)

    if approach not in metrics:
        raise ValueError(f"No metrics for approach {approach}")

    m = metrics[approach]

    return {
        "vehicles": m.vehicle_counts,
        "queue_length": m.queue_length,
        "pedestrians": m.pedestrian_count
    }


# ==============================
# STANDALONE TEST
# ==============================
if __name__ == "__main__":
    video_path = "traffic.mp4"
    tracked = extract_tracked_objects(video_path)
    metrics = build_metrics(tracked)
    traffic_data = build_traffic_data(metrics)

    print("\n🚦 TRAFFIC DATA")
    print(traffic_data)
