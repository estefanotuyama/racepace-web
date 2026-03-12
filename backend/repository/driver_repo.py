from sqlmodel import Session, select

from backend.models.driver import Driver
from backend.models.session_result import SessionResult


def get_drivers_by_session_id(session: Session, session_id: int) -> list[tuple[Driver, SessionResult]]:
    statement = (
        select(Driver, SessionResult)
        .join(SessionResult, SessionResult.driver_id == Driver.id)
        .where(SessionResult.session_id == session_id)
    )
    return session.exec(statement).all()


def get_driver_by_abbreviation(session: Session, abbreviation: str) -> Driver | None:
    return session.exec(select(Driver).where(Driver.abbreviation == abbreviation)).first()


def upsert_driver(session: Session, driver: Driver) -> Driver:
    existing = get_driver_by_abbreviation(session, driver.abbreviation)
    if existing:
        for key, value in driver.model_dump(exclude={"id"}).items():
            setattr(existing, key, value)
        session.add(existing)
        return existing
    session.add(driver)
    session.flush()
    return driver
