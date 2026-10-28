# Multimodal Attendance & Engagement Agent

An offline-first college project prototype built with Python, Streamlit, OpenCV, NumPy, and Pandas.

## Features
- Analyze a recorded classroom video locally.
- Detect faces and maintain short-lived **anonymous** track IDs (not identity recognition).
- Produce attendance candidates based on observed persistence, with manual review labels.
- Plot aggregate face-detection counts and a simple frame-change activity proxy over time.
- Generate heuristic teaching suggestions from session-level trends.
- Store attendance and session summaries as local CSV files in `data/`.

## Important limitations
This is a student-project prototype, not a validated attendance or engagement measurement system. Face detections can be missed or duplicated; temporary track IDs are not reliable identities. The activity metric can respond to camera movement, lighting, or scene changes. It does not measure learning, emotion, or actual attention. Do not use outputs for grading or discipline. Obtain appropriate permission before recording, restrict access to logs, and verify attendance with a human.

## Setup in VS Code (Windows)
1. Install Python 3.10 or newer and VS Code.
2. Extract this ZIP and open the `Multimodal_Attendance_Engagement_Agent` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\\Scripts\\Activate.ps1
   ```

   If PowerShell blocks activation, run the commands below using `cmd` activation instead:
   ` .venv\\Scripts\\activate.bat `

5. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   streamlit run app.py
   ```

7. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Folder structure
```text
Multimodal_Attendance_Engagement_Agent/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── video_analysis.py
│   ├── analytics.py
│   └── storage.py
└── data/
    └── .gitkeep
```

## Suggested demo
Use a short classroom-style video where faces are visible and the camera is stable. Analyze it, review the anonymous track candidates, then download the CSV outputs. You can also demonstrate the dashboard using the generated session logs.

## Future extensions
- Add local audio activity analysis (RMS / voice activity detection) after collecting consent.
- Add a manual teacher confirmation screen to map anonymous tracks to the attendance register.
- Add session comparisons and configurable time windows.
- Add tests and model evaluation using consented, appropriately sourced sample videos.
