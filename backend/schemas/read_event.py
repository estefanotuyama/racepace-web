from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    round_number: int
    country: str
    location: str
    official_event_name: str
    event_name: str
    event_date: datetime
    event_format: str
    year: int


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_name: str
    date: datetime
    round_number: int
    year: int
    f1_api_support: bool
    event_id: int
