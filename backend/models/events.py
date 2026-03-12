from datetime import datetime
from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    __table_args__: ClassVar = (UniqueConstraint("round_number", "year", name="uq_event_round_year"),)

    id: int | None = Field(default=None, primary_key=True)
    round_number: int
    country: str
    location: str
    official_event_name: str
    event_name: str
    event_date: datetime
    event_format: str
    year: int = Field(index=True)
