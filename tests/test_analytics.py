import pandas as pd
from src.analytics import make_teaching_suggestions

def test_suggestions_returns_list():
    timeline = pd.DataFrame({
        "time_seconds": [0, 1, 2, 3, 4, 5, 6, 7],
        "faces_detected": [4, 4, 4, 3, 2, 2, 2, 2],
        "activity_percent": [3, 4, 3, 4, 3, 4, 3, 4],
    })
    result = make_teaching_suggestions({"activity_percent": 3.5}, timeline)
    assert isinstance(result, list)
    assert len(result) > 0
