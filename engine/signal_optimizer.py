"""
Optimize signal timings with safety constraints
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from config.constants import TrafficConstants
from engine.traffic_math import TrafficCalculator, SignalTiming
from detector.traffic_metrics import TrafficMetrics

class SignalOptimizer:
    """Optimize signal timings for all approaches"""

    def __init__(self, area_type: str = 'urban'):
        self.calculator = TrafficCalculator(area_type)

    def optimize_timings(
        self,
        all_metrics: List[TrafficMetrics],
        current_cycle_time: float
    ) -> Tuple[List[SignalTiming], float, Dict]:

        # ================================
        # STEP 1: DEMAND-WEIGHTED GREEN TIME
        # ================================
        total_demand = sum(m.demand_pcu for m in all_metrics)

        # Safety guard: no traffic anywhere
        if total_demand == 0:
            equal_green = current_cycle_time / len(all_metrics)
            required_greens = [
                (m.approach_id, equal_green, m) for m in all_metrics
            ]
        else:
            required_greens = []
            for metrics in all_metrics:
                demand_ratio = metrics.demand_pcu / total_demand

                # Demand dominance weighting
                if demand_ratio >= 0.35:
                    weight = 1.5
                elif demand_ratio >= 0.25:
                    weight = 1.3
                elif demand_ratio >= 0.15:
                    weight = 1.1
                else:
                    weight = 1.0

                base_green = current_cycle_time * demand_ratio * weight

                required_greens.append(
                    (metrics.approach_id, base_green, metrics)
                )

        # ================================
        # STEP 2: SAFETY CONSTRAINTS
        # ================================
        constrained_greens = []
        for approach_id, green_time, metrics in required_greens:
            safe_green = max(TrafficConstants.MIN_GREEN_TIME, green_time)
            safe_green = min(TrafficConstants.MAX_GREEN_TIME, safe_green)

            ped_time = self.calculator.calculate_pedestrian_time(
                metrics.pedestrian_count
            )
            safe_green = max(safe_green, ped_time)

            constrained_greens.append((approach_id, safe_green, metrics))

        # ================================
        # STEP 3: NORMALIZE TO CYCLE TIME
        # ================================
        total_required = sum(green for _, green, _ in constrained_greens)
        total_interphase = len(all_metrics) * (
            TrafficConstants.YELLOW_TIME + TrafficConstants.ALL_RED_TIME
        )

        available_green = current_cycle_time - total_interphase

        if total_required > available_green:
            scale_factor = available_green / total_required
            normalized_greens = []
            for approach_id, green_time, metrics in constrained_greens:
                scaled_green = max(
                    TrafficConstants.MIN_GREEN_TIME,
                    green_time * scale_factor
                )
                normalized_greens.append((approach_id, scaled_green, metrics))
        else:
            normalized_greens = constrained_greens

        # ================================
        # STEP 4: SIGNAL TIMING OBJECTS
        # ================================
        signal_timings = []
        analysis = {
            "spillback_risks": [],
            "congestion_warnings": [],
            "pedestrian_alerts": []
        }

        for approach_id, green_time, metrics in normalized_greens:
            if metrics.check_spillback_risk():
                analysis["spillback_risks"].append({
                    "approach": approach_id,
                    "queue_length": metrics.queue_length,
                    "recommendation": "Consider emergency green extension"
                })
                green_time = min(
                    green_time * 1.3,
                    TrafficConstants.MAX_GREEN_TIME
                )

            if metrics.pedestrian_count > 15:
                analysis["pedestrian_alerts"].append({
                    "approach": approach_id,
                    "pedestrian_count": metrics.pedestrian_count,
                    "message": "High pedestrian activity"
                })

            signal_timings.append(
                SignalTiming(
                    approach_id=approach_id,
                    green_time=round(green_time, 1),
                    pedestrian_time=self.calculator.calculate_pedestrian_time(
                        metrics.pedestrian_count
                    )
                )
            )

        # ================================
        # STEP 5: ACTUAL CYCLE TIME
        # ================================
        actual_cycle = sum(t.total_time() for t in signal_timings)

        return signal_timings, actual_cycle, analysis
