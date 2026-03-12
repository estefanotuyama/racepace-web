from sqlmodel import Session, select

from backend.models.events import Event


def get_events_by_year(session: Session, year: int) -> list[Event]:
    return session.exec(select(Event).where(Event.year == year)).all()


def get_available_years(session: Session) -> list[int]:
    years = session.exec(select(Event.year)).all()
    return sorted(set(years))


def get_event_by_round_and_year(session: Session, round_number: int, year: int) -> Event | None:
    return session.exec(select(Event).where(Event.round_number == round_number, Event.year == year)).first()


def upsert_event(session: Session, event: Event) -> Event:
    existing = get_event_by_round_and_year(session, event.round_number, event.year)
    if existing:
        for key, value in event.model_dump(exclude={"id"}).items():
            setattr(existing, key, value)
        session.add(existing)
        return existing
    session.add(event)
    session.flush()
    return event
