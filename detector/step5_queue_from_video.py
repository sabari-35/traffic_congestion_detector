from detector.object_detector import ObjectDetector
from detector.object_tracker import ObjectTracker
from detector.queue_estimator import QueueEstimator
from detector.video_reader import VideoReader
from detector.roi_mapper import assign_approach

VEHICLE_CLASSES = ["car", "bus", "truck", "motorcycle", "auto"]

tracker = ObjectTracker()
queue_estimator = QueueEstimator()


def build_queue_data_from_video(video_path: str, max_frames: int = 300):
    reader = VideoReader(video_path)
    detector = ObjectDetector()

    # STEP-6 compatible structure
    queue_data = {
        "N": {"vehicles": {}, "queue_length": 0.0, "pedestrians": 0},
        "S": {"vehicles": {}, "queue_length": 0.0, "pedestrians": 0},
        "E": {"vehicles": {}, "queue_length": 0.0, "pedestrians": 0},
        "W": {"vehicles": {}, "queue_length": 0.0, "pedestrians": 0},
    }

    # ✅ Track UNIQUE IDs per approach (CRITICAL FIX)
    seen_vehicle_ids = {k: set() for k in queue_data}
    seen_queued_ids = {k: set() for k in queue_data}
    seen_pedestrian_ids = {k: set() for k in queue_data}

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

        tracked = tracker.update(formatted)

        # Vehicles considered "queued" (low speed / stopped)
        queued_objs = queue_estimator.update(tracked)
        queued_ids = {q["id"] for q in queued_objs}

        for obj in tracked:
            cx, cy = obj["center"]
            approach = assign_approach(cx, cy)
            if approach is None:
                continue

            obj_id = obj["id"]
            label = obj["label"]

            # ----------------------------
            # 🚶 Pedestrians (unique count)
            # ----------------------------
            if label == "person":
                if obj_id not in seen_pedestrian_ids[approach]:
                    seen_pedestrian_ids[approach].add(obj_id)
                    queue_data[approach]["pedestrians"] += 1

            # ----------------------------
            # 🚗 Vehicles (unique count)
            # ----------------------------
            elif label in VEHICLE_CLASSES:
                if obj_id not in seen_vehicle_ids[approach]:
                    seen_vehicle_ids[approach].add(obj_id)
                    queue_data[approach]["vehicles"][label] = (
                        queue_data[approach]["vehicles"].get(label, 0) + 1
                    )

                # ----------------------------
                # 📏 Queue length (unique queued vehicles)
                # ----------------------------
                if obj_id in queued_ids and obj_id not in seen_queued_ids[approach]:
                    seen_queued_ids[approach].add(obj_id)
                    queue_data[approach]["queue_length"] += 5.5  # meters per vehicle

        frame_count += 1

    reader.release()
    return queue_data
