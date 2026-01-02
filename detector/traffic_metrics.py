"""
Process computer vision outputs into structured traffic metrics
"""

from typing import Dict, Optional
from dataclasses import dataclass, field
from config.constants import TrafficConstants


@dataclass
class TrafficMetrics:
    """Structured traffic metrics from computer vision"""

    approach_id: str
    vehicle_counts: Dict[str, int]
    queue_length: float
    lanes: int
    congestion_level: str
    pedestrian_count: int
    current_green_time: float
    link_length: Optional[float] = None

    # ✅ expose demand_pcu (required by optimizer)
    demand_pcu: float = field(init=False)

    def __post_init__(self):
        self.demand_pcu = self.calculate_pcu()

    def calculate_pcu(self) -> float:
        """Convert vehicle counts to PCU"""
        total_pcu = 0.0
        for v_type, count in self.vehicle_counts.items():
            pcu = TrafficConstants.VEHICLE_PCU.get(v_type, 1.0)
            total_pcu += count * pcu
        return total_pcu

    # ✅ ✅ CORRECT PLACE FOR DENSITY
    @property
    def density(self) -> float:
        """
        Vehicle density per lane (PCU / lane)
        """
        return self.demand_pcu / max(self.lanes, 1)

    def get_congestion_factor(self) -> float:
        return TrafficConstants.CONGESTION_LEVELS.get(
            self.congestion_level, 1.0
        )

    def check_spillback_risk(self) -> bool:
        if self.link_length:
            return (
                self.queue_length / self.link_length
            ) >= TrafficConstants.QUEUE_SPILLBACK_RATIO
        return False


# ✅ REQUIRED FOR CHATBOT IMPORTS
class TrafficMetricsProcessor:
    """Convert YOLO / raw input into TrafficMetrics"""

    @staticmethod
    def from_dict(data: Dict) -> TrafficMetrics:
        return TrafficMetrics(
            approach_id=data["approach_id"],
            vehicle_counts=data["vehicle_counts"],
            queue_length=data["queue_length"],
            lanes=data["lanes"],
            congestion_level=data["congestion_level"],
            pedestrian_count=data["pedestrian_count"],
            current_green_time=data["current_green_time"],
            link_length=data.get("link_length"),
        )
