from ultralytics import YOLO
import cv2

# Load YOLO model once
model = YOLO("yolov8n.pt")

# COCO classes we care about
VALID_CLASSES = {
    "car", "bus", "truck", "motorcycle", "person"
}

def run_yolo(video_path="traffic.mp4"):
    cap = cv2.VideoCapture(video_path)
    detections = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=0.4, verbose=False)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]

                if label not in VALID_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detections.append({
                    "label": label,
                    "bbox": (x1, y1, x2, y2)
                })

    cap.release()
    return detections
