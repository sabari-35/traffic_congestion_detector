from detector.visualize_roi import visualize
from detector.step5_queue_from_video import build_queue_data_from_video
from detector.step6_signal_pipeline import run_signal_advisory

VIDEO = "traffic.mp4"

print("STEP 4: VISUALIZATION")
visualize(VIDEO)

print("\nSTEP 5: BUILDING QUEUE DATA FROM VIDEO")
queue_data = build_queue_data_from_video(VIDEO)
print(queue_data)

print("\nSTEP 6: SIGNAL ADVISORY (REAL VIDEO)")
result = run_signal_advisory(queue_data)
print(result)
