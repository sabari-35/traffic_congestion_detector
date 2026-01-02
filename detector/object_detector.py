from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        """
        Returns list of detections:
        {label, bbox}
        """
        results = self.model(frame, verbose=False)[0]
        detections = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append({
                "label": label,
                "bbox": (x1, y1, x2, y2)
            })

        return detections
