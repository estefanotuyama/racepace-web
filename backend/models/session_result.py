from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class SessionResult(SQLModel, table=True):
    __table_args__: ClassVar = (UniqueConstraint("session_id", "driver_id", name="uq_result_session_driver"),)

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="f1session.id", index=True)
    driver_id: int = Field(foreign_key="driver.id", index=True)
    team_name: str = Field(default="")
    team_color: str = Field(default="")
    position: float | None = Field(default=None)
    classified_position: str = Field(default="")
    grid_position: float | None = Field(default=None)
    q1: float | None = Field(default=None)
    q2: float | None = Field(default=None)
    q3: float | None = Field(default=None)
    time: float | None = Field(default=None)
    status: str = Field(default="")
    points: float = Field(default=0.0)
    laps: float | None = Field(default=None)
