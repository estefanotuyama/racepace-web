from typing import Annotated

from fastapi import Depends
from sqlalchemy import distinct
from sqlmodel import select

from backend.db.db_utils import SessionDep
from backend.models.teams import Teams
from backend.models.session_driver import SessionDriver


class TeamRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_all_team_names(self) -> list[str]:
        return list(self.session.exec(select(distinct(SessionDriver.team))))

    def get_existing_team_names(self) -> set[str]:
        return set(self.session.exec(select(Teams.name)))

    def insert_team(self, name: str, color: str) -> None:
        team = Teams(name=name, color=color)
        self.session.add(team)


TeamRepoDep = Annotated[TeamRepository, Depends()]
