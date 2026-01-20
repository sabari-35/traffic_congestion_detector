from detector.video_pipeline import run_video_pipeline

def run_single_camera(approach: str, video_path: str):
    try:
        result = run_video_pipeline(video_path, approach)
        return {
            "status": "ok",
            "approach": approach,
            "data": result
        }
    except Exception as e:
        return {
            "status": "failed",
            "approach": approach,
            "error": str(e)
        }
