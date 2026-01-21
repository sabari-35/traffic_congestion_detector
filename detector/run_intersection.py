from detector.multi_camera_fusion import run_multi_camera_intersection
from detector.step6_signal_pipeline import run_signal_advisory

CAMERAS = {
    "N": "videos/north.mp4",
    "S": "videos/south.mp4",
    "E": "videos/east.mp4",
    "W": "videos/west.mp4"
}

def run_intersection():
    queue_data, failed = run_multi_camera_intersection(CAMERAS)

    if not queue_data:
        return {
            "status": "error",
            "message": "All cameras unavailable"
        }

    decision = run_signal_advisory(queue_data)

    return {
        "status": "partial" if failed else "full",
        "failed_cameras": failed,
        "decision": decision
    }

# THIS IS WHAT YOU ARE MISSING
if __name__ == "__main__":
    print("\n🚦 RUNNING MULTI-CAMERA INTERSECTION\n")
    output = run_intersection()
    print(output)
