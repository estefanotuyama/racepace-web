from pydantic import BaseModel


# DTO — endpoint response for GET /session_result/{session_key}
class DriverPositionResponse(BaseModel):
    position: int | None = None
    team: str
    first_name: str
    last_name: str
    number_of_laps: int | None = 0
    gap_to_leader: float | str | None = None
    duration: float | str | None = None
    dnf: bool
    dns: bool
    dsq: bool


class SessionResultResponse(BaseModel):
    result: list[DriverPositionResponse]
