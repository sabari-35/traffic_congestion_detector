from detector.metrics_builder import build_metrics

sample_assigned = [
    {"label": "car", "approach": "S"},
    {"label": "bus", "approach": "S"},
    {"label": "motorcycle", "approach": "S"},
    {"label": "car", "approach": "E"},
    {"label": "person", "approach": "W"},
]

metrics = build_metrics(sample_assigned)

for k, v in metrics.items():
    print(f"\nApproach {k}")
    print(" Vehicles:", v.vehicle_counts)
    print(" Queue length:", v.queue_length)
    print(" Congestion:", v.congestion_level)
    print(" Pedestrians:", v.pedestrian_count)
