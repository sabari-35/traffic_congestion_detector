class QueueEstimator:
    """
    Speed-based queue detection
    Returns LIST of queued objects (NOT length)
    """

    def __init__(self, speed_threshold=2):
        self.last_positions = {}
        self.speed_threshold = speed_threshold

    def update(self, tracked_objects):
        queued_objects = []

        for obj in tracked_objects:
            obj_id = obj["id"]
            cx, cy = obj["center"]

            if obj_id in self.last_positions:
                px, py = self.last_positions[obj_id]
                speed = abs(cx - px) + abs(cy - py)

                if speed < self.speed_threshold:
                    queued_objects.append(obj)

            self.last_positions[obj_id] = (cx, cy)

        return queued_objects   # ✅ ALWAYS LIST
