from sqlmodel import Session, select

from backend.models.driver import Driver
from backend.models.session_result import SessionResult


def get_results_by_session_id(session: Session, session_id: int) -> list[tuple[SessionResult, Driver]]:
    statement = (
        select(SessionResult, Driver)
        .join(Driver, SessionResult.driver_id == Driver.id)
        .where(SessionResult.session_id == session_id)
        .order_by(SessionResult.position)
    )
    return session.exec(statement).all()


def upsert_result(session: Session, result: SessionResult) -> SessionResult:
    existing = session.exec(
        select(SessionResult).where(
            SessionResult.session_id == result.session_id,
            SessionResult.driver_id == result.driver_id,
        )
    ).first()
    if existing:
        for key, value in result.model_dump(exclude={"id"}).items():
            setattr(existing, key, value)
        session.add(existing)
        return existing
    session.add(result)
    return result
