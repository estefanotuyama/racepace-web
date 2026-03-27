import logging

from sqlmodel import Session, select
from backend.models.session_result import SessionResult
from backend.models.session_driver import SessionDriver

logger = logging.getLogger("racepace")


def insert_session_results(session: Session, session_key: int, results_data: list[dict]) -> int:
    if not results_data:
        return 0

    session_drivers_query = session.exec(
        select(SessionDriver).where(SessionDriver.session_key == session_key)
    )
    driver_map = {sd.driver_number: sd.driver_id for sd in session_drivers_query}

    existing_results_query = session.exec(
        select(SessionResult.driver_id).where(SessionResult.session_key == session_key)
    )
    existing_results_set = set(existing_results_query)

    added = 0
    for datapoint in results_data:
        driver_number = datapoint.get("driver_number")
        driver_id = driver_map.get(driver_number)

        if not driver_id or driver_id in existing_results_set:
            continue

        sr_entry = SessionResult(
            meeting_key=datapoint.get("meeting_key"),
            session_key=datapoint.get("session_key"),
            driver_id=driver_id,
            position=datapoint.get("position"),
            duration=str(datapoint.get("duration")),
            number_of_laps=datapoint.get("number_of_laps"),
            gap_to_leader=str(datapoint.get("gap_to_leader")),
            dnf=datapoint.get("dnf"),
            dns=datapoint.get("dns"),
            dsq=datapoint.get("dsq"),
        )
        session.add(sr_entry)
        added += 1

    logger.info(f"  Results: {added} added")
    return added
