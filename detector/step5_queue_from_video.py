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
        queued_objs = queue_estimator.update(tracked)
        queued_ids = {q["id"] for q in queued_objs}

        for obj in tracked:
            cx, cy = obj["center"]
            approach = assign_approach(cx, cy)
            if approach is None:
                continue

            label = obj["label"]

            if label == "person":
                queue_data[approach]["pedestrians"] += 1

            elif label in VEHICLE_CLASSES:
                queue_data[approach]["vehicles"][label] = (
                    queue_data[approach]["vehicles"].get(label, 0) + 1
                )

                # Increase queue length only for queued vehicles
                if obj["id"] in queued_ids:
                    queue_data[approach]["queue_length"] += 5.5  # avg vehicle length

        frame_count += 1

    reader.release()
    return queue_data
