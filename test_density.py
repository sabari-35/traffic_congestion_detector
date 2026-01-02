from detector.traffic_metrics import TrafficMetrics

m = TrafficMetrics(
    approach_id="N",
    vehicle_counts={"car": 200, "bus": 10},
    queue_length=20,
    lanes=2,
    congestion_level="free",
    pedestrian_count=5,
    current_green_time=30
)

print("PCU:", m.demand_pcu)
print("Density:", m.density)
