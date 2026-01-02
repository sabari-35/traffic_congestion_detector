from detector.yolo_detector import run_yolo
from detector.approach_mapper import assign_approach
from detector.traffic_counter import count_by_approach

detections = run_yolo("traffic.mp4")
assigned = assign_approach(detections)

counts = count_by_approach(assigned)

for approach, data in counts.items():
    print(f"\nApproach {approach}")
    print(" Vehicles:", data["vehicle_counts"])
    print(" Pedestrians:", data["pedestrian_count"])
