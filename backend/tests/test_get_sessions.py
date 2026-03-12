from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
MEETING_KEY = 1236  # MONACO 2024


def test_get_sessions_from_key():
    response = client.get(f"/sessions/{MEETING_KEY}")
    assert response.status_code == 200
    data = response.json()

    print(f"Sessions for meeting key: {MEETING_KEY}")
    for session in data:
        print(
            f"Session Key: {session['session_key']} Session: {session['location']} {session['session_type']} -> {session['session_name']} {session['date']}"
        )
