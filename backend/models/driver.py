from sqlmodel import Field, SQLModel


class Driver(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    driver_number: str
    abbreviation: str = Field(unique=True)
    first_name: str
    last_name: str
    full_name: str
    headshot_url: str = Field(default="")
    country_code: str = Field(default="")
    team_name: str = Field(default="")
    team_color: str = Field(default="")
