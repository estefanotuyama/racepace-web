from sqlmodel import Session, select
from backend.models.events import Event
from backend.models.teams import Teams


def get_events_from_year(session:Session, year: int):
    """
    Queries the database to find all F1 events in a given year.
    :param session: Database session, not related to an F1 session.
    :param year: Year for which you want to find events
    :return: List of events as 'Event' pydantic model.
    """
    return session.exec(select(Event).where(Event.year == year)).all()

def get_available_years(session):
    """
    Queries database to find all unique years so we can display them to users.
    :param session: Database session
    :return: Set with all years.
    """
    years = session.exec(select(Event.year)).all()
    return sorted(set(years))

def get_teams(session):
    teams = session.exec(select(Teams)).all()

    team_map = {team.name : team.color for team in teams}
    return team_map


def get_existing_meeting_keys(session: Session) -> set[int]:
    return set(session.exec(select(Event.meeting_key)).all())


def insert_meeting(session: Session, meeting_data: dict) -> None:
    new_meeting = Event(
        meeting_key=meeting_data.get("meeting_key"),
        circuit_key=meeting_data.get("circuit_key"),
        location=meeting_data.get("location"),
        country_name=meeting_data.get("country_name"),
        circuit_name=meeting_data.get("circuit_short_name"),
        meeting_official_name=meeting_data.get("meeting_official_name"),
        year=meeting_data.get("year"),
    )
    session.add(new_meeting)


def meeting_exists(session: Session, meeting_key: int) -> bool:
    return session.get(Event, meeting_key) is not None
