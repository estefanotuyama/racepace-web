from typing import Annotated

from fastapi import Depends
from sqlalchemy import bindparam
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select

from backend.db.db_utils import SessionDep
from backend.models.session_laps import SessionLaps
from backend.schemas.driver_laps_schema import LapRead
from backend.logging_config import logger


class LapRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_laps_for_driver(self, driver_id: int, session_key: int) -> list[LapRead]:
        laps = self.session.exec(
            select(SessionLaps).where(
                SessionLaps.driver_id == driver_id,
                SessionLaps.session_key == session_key,
            )
        ).all()
        return [
            LapRead(
                lap_number=lap.lap_number,
                time=lap.lap_time,
                speed_trap=lap.st_speed,
                is_pit_out_lap=lap.is_pit_out_lap,
                compound=lap.compound,
            )
            for lap in laps
        ]

    def get_existing_laps_with_compound(self, session_key: int) -> set[tuple[int, int]]:
        rows = self.session.exec(
            select(SessionLaps.driver_id, SessionLaps.lap_number).where(
                (SessionLaps.session_key == session_key) & (SessionLaps.compound != None)
            )
        ).all()
        return {(r[0], r[1]) for r in rows} if rows else set()

    def bulk_upsert_laps(self, values: list[dict]) -> int:
        if not values:
            return 0

        stmt = insert(SessionLaps).values(
            driver_id=bindparam("driver_id"),
            session_key=bindparam("session_key"),
            lap_number=bindparam("lap_number"),
            is_pit_out_lap=bindparam("is_pit_out_lap"),
            lap_time=bindparam("lap_time"),
            st_speed=bindparam("st_speed"),
            compound=bindparam("compound"),
        )

        where_clause_expr = (
            SessionLaps.compound.is_distinct_from(stmt.excluded.compound)
            | SessionLaps.lap_time.is_distinct_from(stmt.excluded.lap_time)
            | SessionLaps.st_speed.is_distinct_from(stmt.excluded.st_speed)
            | SessionLaps.is_pit_out_lap.is_distinct_from(stmt.excluded.is_pit_out_lap)
        )

        do_update = stmt.on_conflict_do_update(
            index_elements=["driver_id", "session_key", "lap_number"],
            set_={
                "is_pit_out_lap": stmt.excluded.is_pit_out_lap,
                "lap_time": stmt.excluded.lap_time,
                "st_speed": stmt.excluded.st_speed,
                "compound": stmt.excluded.compound,
            },
            where=where_clause_expr,
        )

        self.session.execute(do_update, values)
        return len(values)


LapRepoDep = Annotated[LapRepository, Depends()]
