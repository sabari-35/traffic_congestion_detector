import math

class ObjectTracker:
    def __init__(self, max_distance=50):
        self.next_id = 0
        self.objects = {}  # id -> (cx, cy)
        self.max_distance = max_distance

    def update(self, detections):
        updated = {}

        for det in detections:
            cx, cy = det["center"]
            assigned = False

            for obj_id, (ox, oy) in self.objects.items():
                dist = math.hypot(cx - ox, cy - oy)
                if dist < self.max_distance:
                    updated[obj_id] = (cx, cy)
                    det["id"] = obj_id
                    assigned = True
                    break

            if not assigned:
                det["id"] = self.next_id
                updated[self.next_id] = (cx, cy)
                self.next_id += 1

        self.objects = updated
        return detections
