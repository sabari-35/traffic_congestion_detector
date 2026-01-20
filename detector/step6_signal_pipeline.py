from detector.traffic_metrics import TrafficMetrics
from chatbot.traffic_advisor import TrafficAdvisoryChatbot

# ==============================
# IRC-style PCU values
# ==============================
PCU_MAP = {
    "car": 1.0,
    "motorcycle": 0.5,
    "bus": 3.0,
    "truck": 3.0,
    "auto": 1.2,
    "ambulance": 4.0   # 🚑 treat as heavy + priority
}

LANES = {"N": 3, "S": 3, "E": 2, "W": 1}


# ==============================
# PCU + Congestion helpers
# ==============================
def calculate_pcu(vehicle_counts: dict) -> float:
    return round(
        sum(PCU_MAP.get(v, 1.0) * c for v, c in vehicle_counts.items()),
        2
    )


def classify_congestion(pcu_per_lane: float) -> str:
    if pcu_per_lane > 40:
        return "severely_congested"
    elif pcu_per_lane > 25:
        return "congested"
    elif pcu_per_lane > 10:
        return "stable"
    return "free"


# ==============================
# 🚑 Emergency detection
# ==============================
def detect_emergency(queue_data: dict):
    """
    Detect ambulance presence from STEP-5 output
    """
    for approach, data in queue_data.items():
        if data["vehicles"].get("ambulance", 0) > 0:
            return True, approach
    return False, None


# ==============================
# Build TrafficMetrics
# ==============================
def build_metrics_from_queue(queue_data: dict):
    metrics = {}

    for approach, data in queue_data.items():
        lanes = LANES.get(approach, 1)

        base_pcu = calculate_pcu(data["vehicles"])

        # Queue amplification (long queue → higher urgency)
        queue_factor = max(1.0, data["queue_length"] / 10)

        # Pedestrian penalty
        pedestrian_penalty = data["pedestrians"] * 1.5

        total_pcu = (base_pcu * queue_factor) + pedestrian_penalty
        pcu_per_lane = total_pcu / lanes

        congestion = classify_congestion(pcu_per_lane)

        metrics[approach] = TrafficMetrics(
            approach_id=approach,
            vehicle_counts=data["vehicles"],
            queue_length=data["queue_length"],
            lanes=lanes,
            congestion_level=congestion,
            pedestrian_count=data["pedestrians"],
            current_green_time=None  # dynamic
        )

    return metrics


# ==============================
# STEP-6 MAIN ENTRY
# ==============================
def run_signal_advisory(queue_data: dict):
    """
    STEP-6:
    - Detect emergency
    - Build metrics
    - Invoke chatbot with emergency context
    """

    # 🚑 Emergency detection
    emergency_present, emergency_approach = detect_emergency(queue_data)

    # Build metrics
    metrics = build_metrics_from_queue(queue_data)

    chatbot = TrafficAdvisoryChatbot()

    # 🔑 IMPORTANT: pass emergency info explicitly
    decision = chatbot.process_request({
        "approaches": [
            {
                "approach_id": m.approach_id,
                "vehicle_counts": m.vehicle_counts,
                "queue_length": m.queue_length,
                "lanes": m.lanes,
                "congestion_level": m.congestion_level,
                "pedestrian_count": m.pedestrian_count,
                "current_green_time": m.current_green_time,
            }
            for m in metrics.values()
        ],
        "current_cycle_time": 120,
        "emergency_vehicle_present": emergency_present,
        "emergency_approach": emergency_approach
    })

    return {
        "signal_decision": decision,
        "emergency": {
            "present": emergency_present,
            "approach": emergency_approach
        },
        "metrics_snapshot": {
            k: {
                "pcu": calculate_pcu(v.vehicle_counts),
                "congestion": v.congestion_level
            }
            for k, v in metrics.items()
        }
    }
