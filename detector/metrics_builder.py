from detector.traffic_metrics import TrafficMetrics
from detector.queue_estimator import estimate_queue_length, classify_congestion

LANES = {"N": 3, "S": 3, "E": 2, "W": 1}

def build_metrics(assigned_objects):
    metrics = {}

    for approach in ["N", "S", "E", "W"]:
        vehicle_counts = {}
        pedestrian_count = 0

        for obj in assigned_objects:
            if obj["approach"] != approach:
                continue

            if obj["label"] == "person":
                pedestrian_count += 1
            else:
                vehicle_counts[obj["label"]] = (
                    vehicle_counts.get(obj["label"], 0) + 1
                )

        # ✅ 1. Estimate queue length
        queue_length = estimate_queue_length(vehicle_counts)

        # ✅ 2. Temporary metrics to compute density
        temp_metrics = TrafficMetrics(
            approach_id=approach,
            vehicle_counts=vehicle_counts,
            queue_length=queue_length,
            lanes=LANES[approach],
            congestion_level="free",  # placeholder
            pedestrian_count=pedestrian_count,
            current_green_time=30
        )

        density = temp_metrics.density  # PCU per lane

        # ✅ 3. Hybrid congestion classification
        congestion = classify_congestion(queue_length, density)

        # ✅ 4. Final metrics
        metrics[approach] = TrafficMetrics(
            approach_id=approach,
            vehicle_counts=vehicle_counts,
            queue_length=queue_length,
            lanes=LANES[approach],
            congestion_level=congestion,
            pedestrian_count=pedestrian_count,
            current_green_time=30
        )
        print(f"{approach} → Queue={queue_length}m, "f"PCU={temp_metrics.demand_pcu:.1f}, "f"Density={density:.1f}"
)


    return metrics
