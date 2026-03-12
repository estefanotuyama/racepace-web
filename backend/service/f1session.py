from sqlmodel import Session

from backend.repository import event_repo, result_repo, session_repo
from backend.schemas.read_session_result import DriverPosition, ReadSessionResult


def get_sessions(session: Session, year: int, round_number: int):
    event = event_repo.get_event_by_round_and_year(session, round_number, year)
    if not event:
        return []
    return session_repo.get_sessions_by_event_id(session, event.id)


def get_session_result(session: Session, year: int, round_number: int, session_name: str):
    f1session = session_repo.get_session_by_name_round_year(session, session_name, round_number, year)
    if not f1session:
        return ReadSessionResult(result=[])

    results = result_repo.get_results_by_session_id(session, f1session.id)

    driver_positions = [
        DriverPosition(
            position=result.position,
            classified_position=result.classified_position,
            grid_position=result.grid_position,
            team_name=result.team_name,
            team_color=result.team_color,
            first_name=driver.first_name,
            last_name=driver.last_name,
            abbreviation=driver.abbreviation,
            q1=result.q1,
            q2=result.q2,
            q3=result.q3,
            time=result.time,
            status=result.status,
            points=result.points,
            laps=result.laps,
        )
        for result, driver in results
    ]

    return ReadSessionResult(result=driver_positions)
