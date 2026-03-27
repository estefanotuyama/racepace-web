from sqlalchemy import distinct
from sqlmodel import Session, select
from backend.models.teams import Teams
from backend.models.session_driver import SessionDriver


def get_all_team_names(session: Session) -> list[str]:
    return list(session.exec(select(distinct(SessionDriver.team))))


def get_existing_team_names(session: Session) -> set[str]:
    return set(session.exec(select(Teams.name)))


def insert_team(session: Session, name: str, color: str) -> None:
    team = Teams(name=name, color=color)
    session.add(team)
