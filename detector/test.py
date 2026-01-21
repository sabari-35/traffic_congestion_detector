import cv2
import numpy as np
from ultralytics import YOLO
from filterpy.kalman import KalmanFilter
import math
import time

class SortTracker:
    def __init__(self):
        self.trackers = []
        self.track_id = 0

    def add_tracker(self, x, y):
        kf = KalmanFilter(dim_x=4, dim_z=2)
        kf.x = np.array([x, y, 0, 0])
        kf.F = np.array([[1, 0, 1, 0],
                         [0, 1, 0, 1],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])
        kf.H = np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0]])
        kf.P *= 10
        kf.R *= 5
        self.track_id += 1
        return {"id": self.track_id, "kf": kf, "age": 0}

    def update(self, detections):
        objects = []
        for det in detections:
            x, y = det
            matched = False
            for t in self.trackers:
                t["kf"].predict()
                px, py = t["kf"].x[:2]
                if math.hypot(px - x, py - y) < 50:
                    t["kf"].update(np.array([x, y]))
                    t["age"] = 0
                    matched = True
                    objects.append((t["id"], px, py))
                    break
            if not matched:
                new_t = self.add_tracker(x, y)
                new_t["kf"].update(np.array([x, y]))
                self.trackers.append(new_t)
                objects.append((new_t["id"], x, y))

        for t in self.trackers:
            t["age"] += 1

        self.trackers = [t for t in self.trackers if t["age"] < 10]
        return objects

def rule_based_decision(vehicle_count, lane_stats, avg_speed, choke_point_frames):

    actions = []

    if vehicle_count < 8:
        level = "FREE FLOW"
    elif vehicle_count < 15:
        level = "MODERATE"
    elif vehicle_count < 25:
        level = "HEAVY"
    else:
        level = "SEVERE"

    if vehicle_count >= 20:
        actions.append("Increase green signal time by 20 seconds")
        actions.append("Deploy traffic police at junction")

    elif vehicle_count >= 12:
        actions.append("Increase green signal time by 10 seconds")

    if avg_speed < 5 and vehicle_count > 15:
        actions.append("Activate congestion alert system")

    left, mid, right = lane_stats

    if left > mid + 5:
        actions.append("Extend green time for LEFT lane")

    if right > mid + 5:
        actions.append("Extend green time for RIGHT lane")

    if mid > left + 5 and mid > right + 5:
        actions.append("Prioritize MIDDLE lane flow")

    if choke_point_frames > 30:
        actions.append("Open service road / alternate lane")
        actions.append("Enable manual traffic control")

    if not actions:
        actions.append("Traffic is normal – no action required")

    return level, actions

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("traffic_video.mp4")

vehicle_labels = ["car", "motorcycle", "bus", "truck", "bicycle"]

heatmap = None
tracker = SortTracker()

CONGESTION_LIMIT = 10
choke_point_frames = 0

previous_positions = {}
speed_records = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_h, frame_w = frame.shape[:2]

    if heatmap is None:
        heatmap = np.zeros((frame_h, frame_w), dtype=np.float32)

    results = model(frame, stream=True)

    detections = []
    vehicle_count = 0

    left_lane = 0
    mid_lane = 0
    right_lane = 0

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])]
            if label in vehicle_labels:

                vehicle_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                detections.append((cx, cy))
                if cx < frame_w // 3:
                    left_lane += 1
                elif cx < 2 * frame_w // 3:
                    mid_lane += 1
                else:
                    right_lane += 1

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

    tracked = tracker.update(detections)

    speeds = []

    for tid, x, y in tracked:
        x, y = int(x), int(y)

        heatmap[y][x] += 3

        if tid in previous_positions:
            px, py = previous_positions[tid]
            dist = math.hypot(px - x, py - y)
            speeds.append(dist)

        previous_positions[tid] = (x, y)

    avg_speed = sum(speeds)/len(speeds) if speeds else 0

    colored_heatmap = cv2.applyColorMap(
        cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(frame, 0.7, colored_heatmap, 0.3, 0)

    if vehicle_count >= CONGESTION_LIMIT:
        choke_point_frames += 1
    else:
        choke_point_frames = 0

    level, suggestions = rule_based_decision(
        vehicle_count,
        (left_lane, mid_lane, right_lane),
        avg_speed,
        choke_point_frames
    )

    cv2.putText(overlay, f"Vehicles: {vehicle_count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)

    cv2.putText(overlay, f"Level: {level}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,255), 2)

    cv2.putText(overlay, f"Speed Index: {avg_speed:.2f}", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,0,0), 2)

    cv2.putText(overlay, f"Lanes L/M/R: {left_lane}/{mid_lane}/{right_lane}",
                (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,0), 2)

    y = 220
    cv2.putText(overlay, "SYSTEM ACTIONS:", (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)

    for action in suggestions:
        y += 40
        cv2.putText(overlay, action, (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.imshow("SMART TRAFFIC SYSTEM – RULE BASED", overlay)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()