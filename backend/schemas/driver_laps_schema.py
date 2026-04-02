from pydantic import BaseModel


# DTO — endpoint response for GET /laps/{session_key}/{driver_number}
class LapResponse(BaseModel):
    lap_number: int
    time: float
    speed_trap: int
    is_pit_out_lap: bool
    compound: str


class DriverLapsResponse(BaseModel):
    driver_number: int
    first_name: str
    last_name: str
    team: str
    headshot_url: str
    laps: list[LapResponse]
