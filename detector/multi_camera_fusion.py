from detector.run_single_camera import run_single_camera

def run_multi_camera_intersection(camera_map: dict):
    fused_queue_data = {}
    failed_cameras = []

    for approach, video_path in camera_map.items():
        print(f"[INFO] Running {approach} camera")

        result = run_single_camera(approach, video_path)

        if result["status"] == "ok":
            fused_queue_data[approach] = result["data"]
        else:
            failed_cameras.append(approach)
            print(f"[WARN] {approach} camera failed")

    return fused_queue_data, failed_cameras
