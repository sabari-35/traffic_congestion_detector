from detector.traffic_metrics import TrafficMetrics
from chatbot.traffic_advisor import TrafficAdvisoryChatbot

# PCU values (IRC-style)
PCU_MAP = {
    "car": 1.0,
    "motorcycle": 0.5,
    "bus": 3.0,
    "truck": 3.0,
    "auto": 1.2
}

LANES = {"N": 3, "S": 3, "E": 2, "W": 1}


def calculate_pcu(vehicle_counts: dict) -> float:
    pcu = 0.0
    for v_type, count in vehicle_counts.items():
        pcu += PCU_MAP.get(v_type, 1.0) * count
    return round(pcu, 2)


def build_metrics_from_queue(queue_data):
    """
    queue_data format (from STEP 5):
    {
        "N": {"vehicles": {...}, "queue_length": float, "pedestrians": int},
        ...
    }
    """
    metrics = {}

    for approach, data in queue_data.items():
        pcu = calculate_pcu(data["vehicles"])

        # Congestion classification
        if pcu > 300:
            congestion = "severely_congested"
        elif pcu > 150:
            congestion = "congested"
        elif pcu > 50:
            congestion = "stable"
        else:
            congestion = "free"

        metrics[approach] = TrafficMetrics(
            approach_id=approach,
            vehicle_counts=data["vehicles"],
            queue_length=data["queue_length"],
            lanes=LANES[approach],
            congestion_level=congestion,
            pedestrian_count=data["pedestrians"],
            current_green_time=30
        )

    return metrics


def run_signal_advisory(queue_data):
    metrics = build_metrics_from_queue(queue_data)

    chatbot = TrafficAdvisoryChatbot()
    response = chatbot.advise(list(metrics.values()))


    return response
