import json
from pydantic import BaseModel, field_validator


# Internal schema — used by services with field validators for data cleaning
class DriverPosition(BaseModel):
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

    @field_validator('duration', 'gap_to_leader', mode='before')
    @classmethod
    def parse_numbers(cls, v):
        if v == 'None' or v == '' or v is None:
            return None
        elif not v.startswith('['):
            return v
        else:
            valid_json_string = v.replace("None", "null")
            duration_array = json.loads(valid_json_string)
            for duration in reversed(duration_array):
                if duration is not None:
                    return duration
            return None


class ReadSessionResult(BaseModel):
    result: list[DriverPosition]


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
