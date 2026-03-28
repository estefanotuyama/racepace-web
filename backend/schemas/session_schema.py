from pydantic import BaseModel


# DTO — endpoint response for GET /sessions/{meeting_key}
class SessionResponse(BaseModel):
    location: str
    meeting_key: int
    session_key: int
    session_type: str
    session_name: str
    date: str
