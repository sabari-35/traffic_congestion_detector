"""
Main chatbot logic for traffic signal advisory
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

from engine.signal_optimizer import SignalOptimizer
from detector.traffic_metrics import TrafficMetrics, TrafficMetricsProcessor
from config.constants import TrafficConstants


@dataclass
class ChatbotResponse:
    """Structured response from the chatbot"""
    recommended_green_times: Dict[str, float]
    cycle_time: float
    reasoning: List[str]
    safety_confirmation: List[str]
    operational_advice: List[str]
    warnings: List[str]
    timestamp: str


class TrafficAdvisoryChatbot:
    """
    Adaptive Traffic Signal Advisory System
    """

    def __init__(self, area_type: str = "urban"):
        self.optimizer = SignalOptimizer(area_type)
        self.metrics_processor = TrafficMetricsProcessor()

    # ✅ FIXED: advise is now a CLASS METHOD
    def advise(self, metrics: List[TrafficMetrics]) -> ChatbotResponse:
        """
        Wrapper for signal pipeline (used by detector / step6)
        Converts TrafficMetrics → input format → process_request
        """

        input_data = {
            "approaches": [
                {
                    "approach_id": m.approach_id,
                    "vehicle_counts": m.vehicle_counts,
                    "queue_length": m.queue_length,
                    "lanes": m.lanes,
                    "congestion_level": m.congestion_level,
                    "pedestrian_count": m.pedestrian_count,
                    "current_green_time": m.current_green_time,
                    "link_length": m.link_length,
                }
                for m in metrics
            ],
            "current_cycle_time": TrafficConstants.DEFAULT_CYCLE_TIME,
            "emergency_vehicle_present": False,
        }

        return self.process_request(input_data)

    def process_request(self, input_data: Dict[str, Any]) -> ChatbotResponse:
        """Process traffic data and provide advisory"""

        if not self._validate_input(input_data):
            raise ValueError("Invalid input data")

        all_metrics = [TrafficMetrics(**a) for a in input_data["approaches"]]

        timings, cycle_time, analysis = self.optimizer.optimize_timings(
            all_metrics,
            input_data.get(
                "current_cycle_time",
                TrafficConstants.DEFAULT_CYCLE_TIME,
            ),
        )

        return self._build_response(
            timings, cycle_time, analysis, all_metrics, input_data
        )

    def _validate_input(self, data: Dict) -> bool:
        if "approaches" not in data:
            return False

        for a in data["approaches"]:
            for f in [
                "approach_id",
                "vehicle_counts",
                "queue_length",
                "lanes",
                "congestion_level",
                "pedestrian_count",
            ]:
                if f not in a:
                    return False
        return True

    def _build_response(
        self,
        timings,
        cycle_time,
        analysis,
        all_metrics,
        input_data,
    ) -> ChatbotResponse:

        green_times = {t.approach_id: t.green_time for t in timings}

        reasoning = []
        for t in timings:
            m = next(x for x in all_metrics if x.approach_id == t.approach_id)
            reasoning.append(
                f"Approach {t.approach_id}: "
                f"Demand = {m.calculate_pcu():.1f} PCU, "
                f"Congestion = {m.congestion_level}, "
                f"Pedestrians = {m.pedestrian_count}. "
                f"Recommended {t.green_time}s green."
            )

        safety = [
            f"Green times within {TrafficConstants.MIN_GREEN_TIME}s–"
            f"{TrafficConstants.MAX_GREEN_TIME}s limits.",
            f"Pedestrian minimum {TrafficConstants.MIN_PEDESTRIAN_TIME}s ensured.",
            "Cycle time maintains smooth progression.",
        ]

        advice = []
        for r in analysis.get("spillback_risks", []):
            advice.append(
                f"⚠️ Spillback risk on {r['approach']} (queue {r['queue_length']}m)"
            )

        if input_data.get("emergency_vehicle_present"):
            advice.append("🚨 Emergency vehicle detected: override signals")

        warnings = []
        if cycle_time > TrafficConstants.MAX_CYCLE_TIME:
            warnings.append("Cycle time exceeds recommended maximum")

        return ChatbotResponse(
            recommended_green_times=green_times,
            cycle_time=round(cycle_time, 1),
            reasoning=reasoning,
            safety_confirmation=safety,
            operational_advice=advice,
            warnings=warnings,
            timestamp=datetime.now().isoformat(),
        )
