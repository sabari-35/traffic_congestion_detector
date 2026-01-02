from typing import List, Dict
from detector.traffic_metrics import TrafficMetrics
from detector.object_detector import ObjectDetector
from detector.video_reader import VideoReader
from detector.roi_mapper import assign_approach
from config.constants import TrafficConstants

# ==============================
# CONSTANTS (SAFE ENGINEERING)
# ==============================
VEHICLE_LENGTH_M = 5.5  # avg vehicle + gap (meters)
LANES = {"N": 3, "S": 3, "E": 2, "W": 1}


# ==============================
# QUEUE + CONGESTION HELPERS
# ==============================
def estimate_queue_length(vehicle_counts: Dict[str, int]) -> float:
    """
    Estimate queue length (meters) from vehicle count
    """
    total_vehicles = sum(vehicle_counts.values())
    return round(total_vehicles * VEHICLE_LENGTH_M, 1)


def classify_congestion(queue_length: float, density: float) -> str:
    """
    Hybrid congestion classification using:
    - queue length (meters)
    - density (PCU / lane)
    """
    if queue_length > 120 or density > 80:
        return "severely_congested"
    elif queue_length > 80 or density > 50:
        return "congested"
    elif queue_length > 40 or density > 25:
        return "stable"
    else:
        return "free"


# ==============================
# STEP 1: EXTRACT TRACKED OBJECTS
# ==============================
def extract_tracked_objects(video_path, max_frames=100):
    """
    Convert video into tracked_objects list
    """
    reader = VideoReader(video_path)
    detector = ObjectDetector()

    tracked_objects = []
    frame_count = 0

    while True:
        frame = reader.read()
        if frame is None or frame_count >= max_frames:
            break

        detections = detector.detect(frame)

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            approach = assign_approach(cx, cy)
            if approach is None:
                continue

            tracked_objects.append({
                "label": det["label"],
                "approach": approach,
                # Speed retained for future Kalman / SORT integration
                "speed": det.get("speed", 0.0)
            })

        frame_count += 1

    reader.release()
    return tracked_objects


# ==============================
# STEP 2–3: BUILD METRICS
# ==============================
def build_metrics(tracked_objects: List[Dict]) -> Dict[str, TrafficMetrics]:
    """
    Convert tracked objects into TrafficMetrics for each approach
    """
    metrics = {}

    for approach in ["N", "S", "E", "W"]:
        vehicle_counts = {}
        pedestrians = 0

        for obj in tracked_objects:
            if obj.get("approach") != approach:
                continue

            if obj.get("label") == "person":
                pedestrians += 1
            else:
                vehicle_counts[obj["label"]] = (
                    vehicle_counts.get(obj["label"], 0) + 1
                )

        # ------------------------------
        # QUEUE LENGTH (meters)
        # ------------------------------
        queue_length = estimate_queue_length(vehicle_counts)

        # Temporary metrics (PCU calculation only)
        temp_metrics = TrafficMetrics(
            approach_id=approach,
            vehicle_counts=vehicle_counts,
            queue_length=queue_length,
            lanes=LANES[approach],
            congestion_level="free",  # placeholder
            pedestrian_count=pedestrians,
            current_green_time=30
        )

        # ------------------------------
        # DENSITY (PCU per lane)
        # ------------------------------
        density = temp_metrics.demand_pcu / max(LANES[approach], 1)

        # ------------------------------
        # HYBRID CONGESTION
        # ------------------------------
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
# STEP 4: BUILD API JSON
# ==============================
def build_traffic_data(metrics: Dict[str, TrafficMetrics]) -> Dict:
    """
    Convert TrafficMetrics objects into API-ready trafficData JSON
    """
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
# TEST ENTRY POINT
# ==============================
if __name__ == "__main__":
    video_path = "traffic.mp4"

    tracked = extract_tracked_objects(video_path, max_frames=50)
    metrics = build_metrics(tracked)
    traffic_data = build_traffic_data(metrics)

    print(traffic_data)
