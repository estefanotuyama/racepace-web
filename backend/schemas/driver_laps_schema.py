from pydantic import BaseModel, ConfigDict


class LapRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lap_number: int
    time: float | None = None
    speed_trap: float | None = None
    is_pit_out_lap: bool
    compound: str | None = None


class DriverLapsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_number: str
    abbreviation: str
    first_name: str
    last_name: str
    team_name: str
    team_color: str
    headshot_url: str
    laps: list[LapRead]
