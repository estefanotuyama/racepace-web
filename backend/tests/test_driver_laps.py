from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

DRIVER_NUMBER = 16  # CHARLES LECLERC
SESSION_KEY = 9519  # MONACO 2024 QUALIFYING


def test_read_driver_laps():
    response = client.get(f"/laps/{SESSION_KEY}/{DRIVER_NUMBER}")
    assert response.status_code == 200

    data = response.json()

    print(f"Driver lap data: {data}")
