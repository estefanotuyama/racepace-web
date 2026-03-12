from datetime import datetime
from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class F1Session(SQLModel, table=True):
    __table_args__: ClassVar = (
        UniqueConstraint("session_name", "round_number", "year", name="uq_session_name_round_year"),
    )

    id: int | None = Field(default=None, primary_key=True)
    session_name: str
    date: datetime
    round_number: int
    year: int
    f1_api_support: bool
    event_id: int = Field(foreign_key="event.id", index=True)
