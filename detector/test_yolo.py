from detector.yolo_detector import run_yolo

dets = run_yolo("traffic.mp4")

print(dets[:10])
print("Total detections:", len(dets))
