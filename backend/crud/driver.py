import logging

from sqlmodel import Session, select
from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.schemas.read_driver import DriverSessionInfo

logger = logging.getLogger("racepace")

def get_drivers_from_session_key(session: Session, session_key: int) -> list[DriverSessionInfo]:
    """
    Queries the database to find all drivers that participated in an F1 session,
    returning a combined data structure with session-specific info.
    """
    statement = (
        select(Driver, SessionDriver)
        .join(SessionDriver)
        .where(SessionDriver.session_key == session_key)
    )

    results = session.exec(statement).all()

    drivers_info = [
        DriverSessionInfo(
            driver_number=session_link.driver_number,
            team=session_link.team,
            
            first_name=driver.first_name,
            last_name=driver.last_name,
            name_acronym=driver.name_acronym,
            headshot_url=driver.headshot_url,
        )
        for driver, session_link in results
    ]

    return drivers_info

def get_single_driver_from_session_key(session:Session, session_key:int, driver_number:int):
    """
    Queries the database to find a driver that participated in a session.
    :param session: The database session, not related to an F1 session.
    :param session_key: Unique key identifying the session (FP1, Quali, Race, etc.)
    :param driver_number: Driver's number in Formula 1. (Example Charles LeClerc = 16)
    :return: the driver as a pydantic 'Driver' model.
    """

    statement = (
        select(Driver, SessionDriver).
        join(SessionDriver).
        where(
            SessionDriver.session_key == session_key,
            SessionDriver.driver_number == driver_number
        )
    )

    return session.exec(statement).first()


def upsert_drivers_and_links(session: Session, session_key: int, all_drivers_data: list[dict]):
    """
    Adds drivers to the DB if they don't exist and links them to the session.
    Mutates all_drivers_data in-place: adds 'driver_id' key to each dict.
    """
    new_drivers = 0
    acronyms_from_api = {
        d['name_acronym'] for d in all_drivers_data if d.get('name_acronym')
    }

    existing_drivers_query = session.exec(
        select(Driver).where(Driver.name_acronym.in_(acronyms_from_api))
    )

    acronym_driver_map = {driver.name_acronym: driver for driver in existing_drivers_query}

    existing_links_query = session.exec(
        select(SessionDriver.driver_id).where(SessionDriver.session_key == session_key)
    )
    existing_links_set = set(existing_links_query)

    for driver_data in all_drivers_data:
        acronym = driver_data.get('name_acronym')
        if not acronym:
            continue

        driver = acronym_driver_map.get(acronym)

        if driver:
            made_update = False
            new_first_name = driver_data.get('first_name')
            new_last_name = driver_data.get('last_name')
            new_headshot_url = driver_data.get('headshot_url')

            if driver.first_name == "" and new_first_name:
                driver.first_name = new_first_name
                made_update = True

            if driver.last_name == "" and new_last_name:
                driver.last_name = new_last_name
                made_update = True

            if driver.headshot_url == "" and new_headshot_url:
                driver.headshot_url = new_headshot_url
                made_update = True

            if made_update:
                session.add(driver)

        else:
            driver = Driver(
                first_name=driver_data.get('first_name', ""),
                last_name=driver_data.get('last_name', ""),
                name_acronym=acronym,
                headshot_url=driver_data.get('headshot_url', "")
            )
            session.add(driver)
            new_drivers += 1
            acronym_driver_map[acronym] = driver
    session.flush()

    linked = 0
    seen_driver_ids = set()
    for driver_data in all_drivers_data:
        acronym = driver_data.get('name_acronym')
        if not acronym:
            continue
        driver = acronym_driver_map.get(acronym)
        driver_data['driver_id'] = driver.id

        if driver.id not in existing_links_set and driver.id not in seen_driver_ids:
            new_session_driver = SessionDriver(
                session_key=session_key,
                driver_id=driver.id,
                team=driver_data.get('team_name'),
                driver_number=driver_data.get('driver_number')
            )
            session.add(new_session_driver)
            linked += 1
            seen_driver_ids.add(driver.id)
    if new_drivers or linked:
        logger.info(f"  Drivers: {new_drivers} new, {linked} linked to session")
