"""
Optimize signal timings with PRIORITY-FIRST allocation.

Rules:
1. Emergency vehicles get ABSOLUTE priority
2. High demand approaches get green FIRST
3. Pedestrian safety is enforced
4. Spillback risk can extend green
5. Cycle time is strictly respected
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass

from config.constants import TrafficConstants
from engine.traffic_math import TrafficCalculator, SignalTiming
from detector.traffic_metrics import TrafficMetrics


class SignalOptimizer:
    """Optimize signal timings for all approaches"""

    def __init__(self, area_type: str = "urban"):
        self.calculator = TrafficCalculator(area_type)

    def optimize_timings(
        self,
        all_metrics: List[TrafficMetrics],
        current_cycle_time: float
    ) -> Tuple[List[SignalTiming], float, Dict]:

        MIN_GREEN = TrafficConstants.MIN_GREEN_TIME
        MAX_GREEN = TrafficConstants.MAX_GREEN_TIME

        # =====================================================
        #  STEP 0: EMERGENCY OVERRIDE (ABSOLUTE PRIORITY)
        # =====================================================
        emergency_approach = None
        for m in all_metrics:
            if "ambulance" in m.vehicle_counts and m.vehicle_counts["ambulance"] > 0:
                emergency_approach = m.approach_id
                break

        if emergency_approach:
            signal_timings = []
            analysis = {
                "emergency": True,
                "emergency_approach": emergency_approach
            }

            for m in all_metrics:
                if m.approach_id == emergency_approach:
                    green = MAX_GREEN
                else:
                    green = MIN_GREEN

                signal_timings.append(
                    SignalTiming(
                        approach_id=m.approach_id,
                        green_time=green,
                        pedestrian_time=0
                    )
                )

            actual_cycle = sum(t.total_time() for t in signal_timings)
            return signal_timings, round(actual_cycle, 1), analysis

        # =====================================================
        # STEP 1: SORT BY DEMAND (HIGH → LOW)
        # =====================================================
        sorted_metrics = sorted(
            all_metrics,
            key=lambda m: m.demand_pcu,
            reverse=True
        )

        # Interphase time (yellow + all-red)
        total_interphase = len(sorted_metrics) * (
            TrafficConstants.YELLOW_TIME +
            TrafficConstants.ALL_RED_TIME
        )

        available_green = current_cycle_time - total_interphase
        if available_green <= 0:
            raise ValueError("Cycle time too small for interphase")

        total_demand = sum(m.demand_pcu for m in sorted_metrics if m.demand_pcu > 0)

        # =====================================================
        # STEP 2: PRIORITY-FIRST GREEN ALLOCATION
        # =====================================================
        allocations = []
        remaining_green = available_green

        for m in sorted_metrics:
            if remaining_green <= MIN_GREEN:
                break

            if total_demand > 0:
                share = (m.demand_pcu / total_demand) * available_green
            else:
                share = MIN_GREEN

            green = max(MIN_GREEN, min(share, MAX_GREEN))

            # Pedestrian safety
            ped_time = self.calculator.calculate_pedestrian_time(
                m.pedestrian_count
            )
            green = max(green, ped_time)

            green = min(green, remaining_green)

            allocations.append((m.approach_id, green, m))
            remaining_green -= green

        # =====================================================
        # STEP 3: MINIMUM GREEN FOR LEFTOVER APPROACHES
        # =====================================================
        allocated_ids = {a for a, _, _ in allocations}

        for m in sorted_metrics:
            if m.approach_id not in allocated_ids:
                allocations.append((m.approach_id, MIN_GREEN, m))

        # =====================================================
        # STEP 4: BUILD SIGNAL TIMINGS + ANALYSIS
        # =====================================================
        signal_timings = []
        analysis = {
            "spillback_risks": [],
            "pedestrian_alerts": [],
            "priority_order": [m.approach_id for m in sorted_metrics]
        }

        for approach_id, green_time, m in allocations:

            # Spillback override
            if m.check_spillback_risk():
                green_time = min(green_time * 1.3, MAX_GREEN)
                analysis["spillback_risks"].append({
                    "approach": approach_id,
                    "queue_length": m.queue_length,
                    "action": "Green extended due to spillback risk"
                })

            if m.pedestrian_count > 15:
                analysis["pedestrian_alerts"].append({
                    "approach": approach_id,
                    "pedestrians": m.pedestrian_count
                })

            signal_timings.append(
                SignalTiming(
                    approach_id=approach_id,
                    green_time=round(green_time, 1),
                    pedestrian_time=self.calculator.calculate_pedestrian_time(
                        m.pedestrian_count
                    )
                )
            )

        # =====================================================
        # STEP 5: FINAL CYCLE TIME
        # =====================================================
        actual_cycle_time = sum(t.total_time() for t in signal_timings)

        return signal_timings, round(actual_cycle_time, 1), analysis
