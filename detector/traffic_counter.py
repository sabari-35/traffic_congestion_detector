from collections import defaultdict

VEHICLE_CLASSES = {
    "car", "bus", "truck", "motorcycle", "bicycle", "auto"
}

def count_by_approach(assigned_objects):
    """
    Input: list of {label, approach}
    Output: dict keyed by approach
    """

    counts = {}

    for approach in ["N", "S", "E", "W"]:
        counts[approach] = {
            "vehicle_counts": defaultdict(int),
            "pedestrian_count": 0
        }

    for obj in assigned_objects:
        approach = obj["approach"]
        label = obj["label"]

        if label == "person":
            counts[approach]["pedestrian_count"] += 1
        elif label in VEHICLE_CLASSES:
            counts[approach]["vehicle_counts"][label] += 1

    # convert defaultdict → normal dict
    for a in counts:
        counts[a]["vehicle_counts"] = dict(counts[a]["vehicle_counts"])

    return counts
