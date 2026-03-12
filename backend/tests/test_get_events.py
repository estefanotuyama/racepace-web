from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
YEAR = 2024


def test_get_events_by_year():
    response = client.get(f"/events/{YEAR}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("meeting_key" in event for event in data)

    print(f"{YEAR} Events:")
    for event in data:
        print(f"{event['meeting_official_name']} -> Meeting Key: {event['meeting_key']}")
