from sqlmodel import Session, select

from backend.models.session_laps import SessionLaps


def get_laps_by_session_and_driver(session: Session, session_id: int, driver_id: int) -> list[SessionLaps]:
    return session.exec(
        select(SessionLaps)
        .where(SessionLaps.session_id == session_id, SessionLaps.driver_id == driver_id)
        .order_by(SessionLaps.lap_number)
    ).all()


def upsert_lap(session: Session, lap: SessionLaps) -> SessionLaps:
    existing = session.exec(
        select(SessionLaps).where(
            SessionLaps.session_id == lap.session_id,
            SessionLaps.driver_id == lap.driver_id,
            SessionLaps.lap_number == lap.lap_number,
        )
    ).first()
    if existing:
        for key, value in lap.model_dump(exclude={"id"}).items():
            setattr(existing, key, value)
        session.add(existing)
        return existing
    session.add(lap)
    return lap
