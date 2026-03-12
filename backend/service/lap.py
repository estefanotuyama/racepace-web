from sqlmodel import Session

from backend.repository import driver_repo, lap_repo, session_repo


def get_driver_lap_times(session: Session, year: int, round_number: int, session_name: str, driver_abbreviation: str):
    f1session = session_repo.get_session_by_name_round_year(session, session_name, round_number, year)
    if not f1session:
        return None, []

    driver = driver_repo.get_driver_by_abbreviation(session, driver_abbreviation)
    if not driver:
        return None, []

    laps = lap_repo.get_laps_by_session_and_driver(session, f1session.id, driver.id)
    return driver, laps
