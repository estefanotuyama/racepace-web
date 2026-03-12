from sqlmodel import Session

from backend.repository import event_repo, team_repo


def get_events_from_year(session: Session, year: int):
    return event_repo.get_events_by_year(session, year)


def get_available_years(session: Session):
    return event_repo.get_available_years(session)


def get_teams(session: Session):
    teams = team_repo.get_all_teams(session)
    return {team.name: team.color for team in teams}
