from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class SessionLaps(SQLModel, table=True):
    __table_args__: ClassVar = (UniqueConstraint("session_id", "driver_id", "lap_number", name="uq_lap"),)

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="f1session.id", index=True)
    driver_id: int = Field(foreign_key="driver.id", index=True)
    driver_abbreviation: str
    driver_number: str
    lap_number: int
    lap_time: float | None = Field(default=None)
    stint: int = Field(default=0)
    pit_out_time: float | None = Field(default=None)
    pit_in_time: float | None = Field(default=None)
    sector1_time: float | None = Field(default=None)
    sector2_time: float | None = Field(default=None)
    sector3_time: float | None = Field(default=None)
    speed_i1: float | None = Field(default=None)
    speed_i2: float | None = Field(default=None)
    speed_fl: float | None = Field(default=None)
    speed_st: float | None = Field(default=None)
    is_personal_best: bool = Field(default=False)
    compound: str | None = Field(default=None)
    tyre_life: float | None = Field(default=None)
    fresh_tyre: bool | None = Field(default=None)
    track_status: str = Field(default="")
    position: float | None = Field(default=None)
    deleted: bool | None = Field(default=None)
    is_accurate: bool = Field(default=True)
