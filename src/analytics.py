def build_session_summary(result):
    return result.get("summary", {})

def make_teaching_suggestions(summary, timeline):
    suggestions = []
    if timeline is None or timeline.empty:
        return ["Collect a longer, well-lit recording and review the results manually."]
    mean_activity = float(timeline["activity_percent"].mean())
    face_counts = timeline["faces_detected"]
    if len(face_counts) >= 4:
        window = max(1, len(face_counts) // 4)
        first = float(face_counts.iloc[:window].mean())
        last = float(face_counts.iloc[-window:].mean())
        if first > 0 and last < first * 0.7:
            suggestions.append("Visible detections decreased toward the end. Consider a short recap or interactive question, then verify the room conditions.")
        elif last > first * 1.25:
            suggestions.append("More visible detections appeared near the end. Check whether a transition, group activity, or camera movement explains this pattern.")
    if mean_activity < 2:
        suggestions.append("The video had low frame-change activity. This may reflect a still camera or lecture format; consider a quick poll or think-pair-share if appropriate.")
    elif mean_activity > 20:
        suggestions.append("Frame-change activity was high. Check for camera motion or transitions before interpreting it; a structured activity may help if the room was genuinely busy.")
    if not suggestions:
        suggestions.append("No strong aggregate trend was detected. Try periodic comprehension checks and compare with learner feedback.")
    suggestions.append("Treat these as prompts for teacher reflection, not as a measurement of individual attention or learning.")
    return suggestions
