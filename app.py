import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.video_analysis import analyze_video
from src.analytics import build_session_summary, make_teaching_suggestions
from src.storage import ensure_data_dir, save_attendance, save_session

st.set_page_config(page_title="Classroom Intelligence", page_icon="🎓", layout="wide")
ensure_data_dir()

st.title("🎓 Multimodal Attendance & Engagement Agent")
st.caption("Offline-first classroom analytics prototype • no face recognition or cloud upload")

with st.sidebar:
    st.header("Session setup")
    session_name = st.text_input("Session / subject", "Demo Classroom Session")
    min_presence = st.slider("Minimum observed presence (seconds)", 1, 60, 5)
    sample_every = st.slider("Analyze every Nth video frame", 1, 15, 3)
    st.info("Prototype note: the demo detects faces locally but does not identify people. Attendance labels are anonymous track IDs and should be reviewed by a teacher.")

tab1, tab2, tab3, tab4 = st.tabs(["Video analysis", "Session dashboard", "Attendance logs", "About & privacy"])

with tab1:
    st.subheader("Analyze a recorded classroom video")
    video = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov", "mkv"])
    st.write("Supported analysis: anonymous face-track persistence, movement/activity proxy, and time-window trends.")
    if video and st.button("Analyze video", type="primary"):
        temp_path = Path("data") / f"uploaded_{video.name.replace('/', '_').replace('\\\\', '_')}"
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_bytes(video.getbuffer())
        with st.spinner("Analyzing locally on this computer..."):
            try:
                result = analyze_video(str(temp_path), sample_every=sample_every, min_presence=min_presence)
                st.session_state["last_result"] = result
                st.session_state["last_session_name"] = session_name
                save_attendance(result["attendance"], session_name)
                save_session(result["summary"], session_name)
                st.success("Analysis complete. Results saved locally in the data/ folder.")
            except Exception as e:
                st.error(f"Could not analyze this video: {e}")
                st.info("Try an MP4/MOV file encoded with a common codec.")
            finally:
                try: temp_path.unlink(missing_ok=True)
                except Exception: pass

    result = st.session_state.get("last_result")
    if result:
        st.markdown("### Latest analysis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Anonymous tracks observed", result["summary"]["tracks_observed"])
        c2.metric("Video duration", f'{result["summary"]["duration_seconds"]:.1f} s')
        c3.metric("Activity proxy", f'{result["summary"]["activity_percent"]:.1f}%')
        st.dataframe(result["attendance"], use_container_width=True)
        st.line_chart(result["timeline"].set_index("time_seconds")[["faces_detected", "activity_percent"]])
        st.download_button("Download attendance CSV", result["attendance"].to_csv(index=False), "attendance.csv", "text/csv")
        st.download_button("Download timeline CSV", result["timeline"].to_csv(index=False), "engagement_timeline.csv", "text/csv")
        st.markdown("### Teaching suggestions (heuristic, not a judgment of any student)")
        for suggestion in make_teaching_suggestions(result["summary"], result["timeline"]):
            st.write(f"• {suggestion}")

with tab2:
    st.subheader("Session dashboard")
    sessions_file = Path("data/session_summaries.csv")
    if sessions_file.exists():
        sessions = pd.read_csv(sessions_file)
        if not sessions.empty:
            st.dataframe(sessions, use_container_width=True)
            numeric = [c for c in ["tracks_observed", "duration_seconds", "activity_percent"] if c in sessions.columns]
            if numeric:
                st.bar_chart(sessions.set_index("session_name")[numeric])
        else:
            st.info("No sessions recorded yet. Analyze a video to populate the dashboard.")
    else:
        st.info("No sessions recorded yet. Analyze a video to populate the dashboard.")

with tab3:
    st.subheader("Locally stored attendance")
    attendance_file = Path("data/attendance_logs.csv")
    if attendance_file.exists():
        logs = pd.read_csv(attendance_file)
        if not logs.empty:
            st.dataframe(logs, use_container_width=True)
            st.download_button("Download all attendance logs", logs.to_csv(index=False), "attendance_logs.csv", "text/csv")
        else:
            st.info("Attendance log is empty.")
    else:
        st.info("Attendance log is empty.")

with tab4:
    st.subheader("Project scope")
    st.markdown("""
- **Attendance:** tracks how long anonymous visual detections persist in the video.
- **Engagement proxy:** estimates visible activity from frame-to-frame changes and face counts.
- **Suggestions:** offers general session-level teaching ideas based on aggregate trends.
- **Offline design:** processing and CSV storage happen on the local machine.
- **Privacy:** no face recognition, emotion inference, identity matching, or cloud API calls.

**Important limitation:** head direction, facial expression, and movement cannot reliably prove attention or learning. Results are approximate session-level signals, not grades or disciplinary evidence. A teacher should verify attendance manually and inform participants before recording.
""")
    st.subheader("Run locally")
    st.code("python -m venv .venv\\n# Windows: .venv\\\\Scripts\\\\activate\\n# macOS/Linux: source .venv/bin/activate\\npip install -r requirements.txt\\nstreamlit run app.py", language="bash")
