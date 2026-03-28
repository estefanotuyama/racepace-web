from pydantic import BaseModel


# Internal schemas — used by services to represent domain data
class LapRead(BaseModel):
    lap_number: int | None = None
    time: float | None = None
    speed_trap: int | None = None
    is_pit_out_lap: bool | None = None
    compound: str | None = None


class DriverLapsRead(BaseModel):
    driver_number: int
    first_name: str
    last_name: str
    team: str
    headshot_url: str
    laps: list[LapRead]


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
