from sqlmodel import Session, select

from backend.models.teams import Teams


def get_all_teams(session: Session) -> list[Teams]:
    return session.exec(select(Teams)).all()


def upsert_team(session: Session, team: Teams) -> Teams:
    existing = session.exec(select(Teams).where(Teams.name == team.name)).first()
    if existing:
        existing.color = team.color
        session.add(existing)
        return existing
    session.add(team)
    return team
