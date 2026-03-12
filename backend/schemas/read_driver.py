from pydantic import BaseModel, ConfigDict


class DriverSessionInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_number: str
    abbreviation: str
    first_name: str
    last_name: str
    full_name: str
    headshot_url: str
    team_name: str
    team_color: str
