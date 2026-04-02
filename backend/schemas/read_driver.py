from pydantic import BaseModel


# DTO — endpoint response for GET /drivers/{session_key}
class DriverResponse(BaseModel):
    driver_number: int
    team: str | None = None
    first_name: str
    last_name: str
    name_acronym: str
    headshot_url: str
