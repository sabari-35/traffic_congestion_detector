from detector.yolo_detector import run_yolo
from detector.approach_mapper import assign_approach

dets = run_yolo("traffic.mp4")
assigned = assign_approach(dets)

print("Sample assigned objects:")
for obj in assigned[:10]:
    print(obj)

print("Total assigned:", len(assigned))
