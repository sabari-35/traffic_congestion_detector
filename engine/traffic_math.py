"""
Core traffic engineering calculations
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from config.constants import TrafficConstants
from detector.traffic_metrics import TrafficMetrics

@dataclass
class SignalTiming:
    approach_id: str
    green_time: float
    yellow_time: float = TrafficConstants.YELLOW_TIME
    all_red_time: float = TrafficConstants.ALL_RED_TIME
    pedestrian_time: float = 0
    
    def total_time(self) -> float:
        return self.green_time + self.yellow_time + self.all_red_time

class TrafficCalculator:
    """Perform traffic engineering calculations"""
    
    def __init__(self, area_type: str = 'urban'):
        self.saturation_flow = TrafficConstants.SATURATION_FLOW[area_type]
        
    def calculate_demand_flow(self, metrics: TrafficMetrics) -> float:
        """Calculate demand flow rate (PCU/hour)"""
        pcu_count = metrics.calculate_pcu()
        # Assuming observation period of signal cycle
        demand_flow = (pcu_count / metrics.current_green_time) * 3600
        return demand_flow
    
    def calculate_required_green_time(
        self,
        metrics: TrafficMetrics,
        cycle_time: float,
        lost_time: float = 4.0
    ) -> float:
        """
        Calculate required green time using Webster's method
        
        Formula: g = (v/s) * (C - L)
        where:
        g = green time
        v = demand flow
        s = saturation flow
        C = cycle time
        L = total lost time
        """
        demand_flow = self.calculate_demand_flow(metrics)
        demand_capacity_ratio = demand_flow / (self.saturation_flow * metrics.lanes)
        
        effective_green = demand_capacity_ratio * (cycle_time - lost_time)
        
        # Apply congestion adjustment
        congestion_factor = metrics.get_congestion_factor()
        adjusted_green = effective_green * congestion_factor
        
        return adjusted_green
    
    def calculate_pedestrian_time(self, pedestrian_count: int, crosswalk_width: float = 10.0) -> float:
        """Calculate minimum pedestrian crossing time"""
        min_time = TrafficConstants.MIN_PEDESTRIAN_TIME
        if pedestrian_count > 20:
            # Add extra time for large groups
            additional_time = (pedestrian_count - 20) * 0.1
            min_time += min(additional_time, 10)  # Max additional 10 seconds
        return min_time