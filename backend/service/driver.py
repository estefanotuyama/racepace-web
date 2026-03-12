from sqlmodel import Session

from backend.repository import driver_repo, session_repo
from backend.schemas.read_driver import DriverSessionInfo


def get_drivers_for_session(
    session: Session, year: int, round_number: int, session_name: str
) -> list[DriverSessionInfo]:
    f1session = session_repo.get_session_by_name_round_year(session, session_name, round_number, year)
    if not f1session:
        return []

    rows = driver_repo.get_drivers_by_session_id(session, f1session.id)

    return [
        DriverSessionInfo(
            driver_number=driver.driver_number,
            abbreviation=driver.abbreviation,
            first_name=driver.first_name,
            last_name=driver.last_name,
            full_name=driver.full_name,
            headshot_url=driver.headshot_url,
            team_name=result.team_name,
            team_color=result.team_color,
        )
        for driver, result in rows
    ]
