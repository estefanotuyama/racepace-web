from sqlmodel import Session, select

from backend.models.sessions import F1Session


def get_sessions_by_event_id(session: Session, event_id: int) -> list[F1Session]:
    return session.exec(select(F1Session).where(F1Session.event_id == event_id)).all()


def get_session_by_name_round_year(
    session: Session, session_name: str, round_number: int, year: int
) -> F1Session | None:
    return session.exec(
        select(F1Session).where(
            F1Session.session_name == session_name,
            F1Session.round_number == round_number,
            F1Session.year == year,
        )
    ).first()


def upsert_session(session: Session, f1session: F1Session) -> F1Session:
    existing = get_session_by_name_round_year(session, f1session.session_name, f1session.round_number, f1session.year)
    if existing:
        for key, value in f1session.model_dump(exclude={"id"}).items():
            setattr(existing, key, value)
        session.add(existing)
        return existing
    session.add(f1session)
    session.flush()
    return f1session
