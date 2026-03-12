from pydantic import BaseModel, ConfigDict


class DriverPosition(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: float | None = None
    classified_position: str = ""
    grid_position: float | None = None
    team_name: str
    team_color: str
    first_name: str
    last_name: str
    abbreviation: str
    q1: float | None = None
    q2: float | None = None
    q3: float | None = None
    time: float | None = None
    status: str = ""
    points: float = 0.0
    laps: float | None = None


class ReadSessionResult(BaseModel):
    result: list[DriverPosition]
