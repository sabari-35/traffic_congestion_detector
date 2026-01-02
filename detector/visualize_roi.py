import cv2
import numpy as np
from ultralytics import YOLO
from detector.roi_config import ROIS
from detector.object_tracker import ObjectTracker
from detector.queue_estimator import QueueEstimator

# ✅ INIT TRACKER & QUEUE ESTIMATOR (ONCE)
tracker = ObjectTracker()
queue_estimator = QueueEstimator()

COLORS = {
    "N": (255, 0, 0),
    "S": (0, 255, 0),
    "E": (0, 0, 255),
    "W": (255, 255, 0),
}

def point_in_polygon(point, polygon):
    return cv2.pointPolygonTest(polygon, point, False) >= 0


def visualize(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Cannot open video")
        return

    # ✅ LOAD YOLO ONCE
    model = YOLO("yolov8n.pt")

    print("🎥 YOLO + ROI + TRACKING + QUEUE (STABLE)")
    print("➡ Press Q or ESC to exit")

    window = "Traffic ROI"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, 1280, 720)

    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_id += 1

        # 🔴 FRAME SKIP (VERY IMPORTANT FOR PERFORMANCE)
        if frame_id % 5 != 0:
            continue

        # ===============================
        # 1️⃣ YOLO DETECTION
        # ===============================
        results = model(frame, conf=0.4, verbose=False)[0]

        detections = []

        for box in results.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            if label not in ["car", "bus", "truck", "motorcycle", "person"]:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            detections.append({
                "bbox": (x1, y1, x2, y2),
                "center": (cx, cy),
                "label": label
            })

        # ===============================
        # 2️⃣ TRACK OBJECTS (ID ASSIGNMENT)
        # ===============================
        tracked = tracker.update(detections)

        # ===============================
        # 3️⃣ QUEUE ESTIMATION (STOPPED VEHICLES)
        # ===============================
        queue_objects = queue_estimator.update(tracked)
        queue_ids = {obj["id"] for obj in queue_objects}

        # ===============================
        # 4️⃣ DRAW ROIs
        # ===============================
        for approach, pts in ROIS.items():
            poly = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [poly], True, COLORS[approach], 3)
            cv2.putText(
                frame,
                approach,
                tuple(poly[0][0]),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                COLORS[approach],
                2
            )

        # ===============================
        # 5️⃣ DRAW TRACKED OBJECTS
        # ===============================
        for obj in tracked:
            x1, y1, x2, y2 = obj["bbox"]
            cx, cy = obj["center"]
            label = obj["label"]
            obj_id = obj["id"]

            for approach, pts in ROIS.items():
                if point_in_polygon((cx, cy), pts):

                    # 🔴 QUEUE VEHICLE → RED
                    if obj_id in queue_ids:
                        color = (0, 0, 255)
                        text = f"ID {obj_id} QUEUE"
                    else:
                        color = COLORS[approach]
                        text = f"{label}-{approach}-ID{obj_id}"

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        frame,
                        text,
                        (x1, y1 - 7),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2
                    )
                    break

        cv2.imshow(window, frame)

        key = cv2.waitKey(1)
        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Visualization closed")
