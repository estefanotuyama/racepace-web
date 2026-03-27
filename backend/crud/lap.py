from sqlalchemy import bindparam
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select
from backend.models.session_laps import SessionLaps
from backend.crud.driver import get_single_driver_from_session_key

from backend.logging_config import logger


def get_driver_lap_times(session: Session, session_key: int, driver_number: int):
    """
    Queries database for all of a driver's lap times in a given F1 session.
    :param session: Database session, not related to an F1 session.
    :param session_key: Unique key identifying the session (FP1, Quali, Race, etc.)
    :param driver_number: Driver's number in Formula 1. (Example Charles LeClerc = 16)
    :return: driver, as a 'Driver' pydantic model, and a list of laps, each a 'SessionLaps' pydantic model.
    """
    driver_data = get_single_driver_from_session_key(session, session_key, driver_number)

    if not driver_data:
        return None, None, []

    driver, session_data = driver_data

    laps = session.exec(select(SessionLaps).where(
        SessionLaps.driver_id == driver.id,
        SessionLaps.session_key == session_key
    )).all()

    return driver, session_data, laps


def get_existing_laps_with_compound(session: Session, session_key: int) -> set[tuple[int, int]]:
    rows = session.exec(
        select(SessionLaps.driver_id, SessionLaps.lap_number).where(
            (SessionLaps.session_key == session_key) & (SessionLaps.compound != None)
        )
    ).all()
    return {(r[0], r[1]) for r in rows} if rows else set()


def bulk_upsert_laps(session: Session, values: list[dict]) -> int:
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

    session.execute(do_update, values)
    return len(values)
