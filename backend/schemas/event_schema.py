from pydantic import BaseModel


# Internal schema
class EventRead(BaseModel):
    meeting_key: int
    circuit_key: int
    location: str
    country_name: str
    circuit_name: str
    meeting_official_name: str
    year: int


# DTO — endpoint response for GET /events/{year}
class EventResponse(BaseModel):
    meeting_key: int
    circuit_key: int
    location: str
    country_name: str
    circuit_name: str
    meeting_official_name: str
    year: int
