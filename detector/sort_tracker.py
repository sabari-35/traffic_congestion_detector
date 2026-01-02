import math
import numpy as np
from filterpy.kalman import KalmanFilter

class SortTracker:
    def __init__(self, max_age=10, match_distance=50):
        self.trackers = []
        self.track_id = 0
        self.max_age = max_age
        self.match_distance = match_distance

    def _create_tracker(self, x, y):
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
        return {
            "id": self.track_id,
            "kf": kf,
            "age": 0,
            "last_pos": (x, y)
        }

    def update(self, detections):
        """
        detections: list of dicts
        { "center": (x,y), "label": str }
        """
        tracked_objects = []

        for det in detections:
            x, y = det["center"]
            label = det["label"]
            matched = False

            for t in self.trackers:
                t["kf"].predict()
                px, py = t["kf"].x[:2]

                if math.hypot(px - x, py - y) < self.match_distance:
                    t["kf"].update(np.array([x, y]))
                    speed = math.hypot(x - t["last_pos"][0], y - t["last_pos"][1])
                    t["last_pos"] = (x, y)
                    t["age"] = 0

                    tracked_objects.append({
                        "id": t["id"],
                        "center": (x, y),
                        "speed": speed,
                        "label": label
                    })
                    matched = True
                    break

            if not matched:
                t = self._create_tracker(x, y)
                tracked_objects.append({
                    "id": t["id"],
                    "center": (x, y),
                    "speed": 0.0,
                    "label": label
                })
                self.trackers.append(t)

        for t in self.trackers:
            t["age"] += 1

        self.trackers = [t for t in self.trackers if t["age"] < self.max_age]

        return tracked_objects
