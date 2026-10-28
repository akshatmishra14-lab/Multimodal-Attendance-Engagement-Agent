from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")

def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_attendance(attendance, session_name):
    ensure_data_dir()
    if attendance is None or attendance.empty:
        return
    frame = attendance.copy()
    frame.insert(0, "session_name", session_name)
    frame.insert(1, "recorded_at", pd.Timestamp.now().isoformat(timespec="seconds"))
    path = DATA_DIR / "attendance_logs.csv"
    frame.to_csv(path, mode="a", header=not path.exists(), index=False)

def save_session(summary, session_name):
    ensure_data_dir()
    row = {"session_name": session_name, **summary}
    path = DATA_DIR / "session_summaries.csv"
    pd.DataFrame([row]).to_csv(path, mode="a", header=not path.exists(), index=False)
