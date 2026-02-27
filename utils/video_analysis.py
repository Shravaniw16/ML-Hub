import cv2
import math

def analyze_video(filepath):
    cap = cv2.VideoCapture(filepath)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    # Safety fallback
    if frame_count <= 0 or math.isnan(frame_count):
        frame_count = int(fps * cap.get(cv2.CAP_PROP_POS_MSEC) / 1000) if fps else 0

    duration = frame_count / fps if fps else 0

    cap.release()

    return {
        "resolution": f"{width}x{height}",
        "fps": round(fps, 2),
        "total_frames": int(frame_count),
        "duration_seconds": round(duration, 2)
    }
