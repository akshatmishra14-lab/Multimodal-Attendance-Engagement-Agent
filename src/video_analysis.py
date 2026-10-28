from collections import defaultdict
from pathlib import Path
import cv2
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_video(video_path, sample_every=3, min_presence=5):
    """Local, anonymous face detection and simple movement proxy."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Video file could not be opened.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = float(total_frames / fps) if total_frames else 0.0
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        cap.release()
        raise RuntimeError("OpenCV face detector could not be loaded.")

    tracks = {}
    next_id = 1
    previous_gray = None
    timeline = []
    frame_index = 0
    sample_every = max(1, int(sample_every))

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index % sample_every != 0:
            frame_index += 1
            continue
        time_sec = frame_index / fps
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(35, 35))
        # Greedy centroid matching creates temporary anonymous track IDs.
        centers = [(int(x + w/2), int(y + h/2), int(w), int(h)) for x, y, w, h in faces]
        used = set()
        for cx, cy, w, h in centers:
            best_id, best_dist = None, 10**9
            for tid, t in tracks.items():
                if tid in used or time_sec - t["last_seen"] > 2.5:
                    continue
                tx, ty = t["center"]
                dist = (cx-tx)**2 + (cy-ty)**2
                limit = max(80**2, (w+h)**2)
                if dist < limit and dist < best_dist:
                    best_id, best_dist = tid, dist
            if best_id is None:
                best_id = next_id
                next_id += 1
                tracks[best_id] = {"first_seen": time_sec, "last_seen": time_sec, "center": (cx, cy), "samples": 0}
            t = tracks[best_id]
            t["last_seen"] = time_sec
            t["center"] = (cx, cy)
            t["samples"] += 1
            used.add(best_id)

        activity = 0.0
        if previous_gray is not None:
            small_a = cv2.resize(previous_gray, (160, 90))
            small_b = cv2.resize(gray, (160, 90))
            diff = cv2.absdiff(small_a, small_b)
            activity = float(np.mean(diff > 18) * 100)
        previous_gray = gray
        timeline.append({
            "time_seconds": round(time_sec, 2),
            "faces_detected": int(len(faces)),
            "activity_percent": round(activity, 2)
        })
        frame_index += 1
    cap.release()

    sampled_interval = sample_every / fps
    rows = []
    for tid, t in tracks.items():
        observed = max(0.0, t["last_seen"] - t["first_seen"] + sampled_interval)
        rows.append({
            "anonymous_track_id": f"Track-{tid:03d}",
            "first_seen_seconds": round(t["first_seen"], 2),
            "last_seen_seconds": round(t["last_seen"], 2),
            "observed_seconds": round(observed, 2),
            "attendance_candidate": "Review" if observed >= min_presence else "Short detection - review"
        })
    attendance = pd.DataFrame(rows, columns=[
        "anonymous_track_id", "first_seen_seconds", "last_seen_seconds", "observed_seconds", "attendance_candidate"
    ])
    timeline_df = pd.DataFrame(timeline, columns=["time_seconds", "faces_detected", "activity_percent"])
    activity_percent = float(timeline_df["activity_percent"].mean()) if not timeline_df.empty else 0.0
    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tracks_observed": int(len(rows)),
        "duration_seconds": round(duration if duration else (timeline[-1]["time_seconds"] if timeline else 0), 2),
        "activity_percent": round(activity_percent, 2),
        "average_faces_per_sample": round(float(timeline_df["faces_detected"].mean()), 2) if not timeline_df.empty else 0.0
    }
    return {"attendance": attendance, "timeline": timeline_df, "summary": summary}
