from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from backend.db.db_utils import SessionDep
from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.logging_config import logger


class DriverRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_drivers_from_session_key(self, session_key: int):
        statement = (
            select(Driver, SessionDriver)
            .join(SessionDriver)
            .where(SessionDriver.session_key == session_key)
        )
        return self.session.exec(statement).all()

    def get_single_driver_from_session_key(self, session_key: int, driver_number: int):
        statement = (
            select(Driver, SessionDriver)
            .join(SessionDriver)
            .where(
                SessionDriver.session_key == session_key,
                SessionDriver.driver_number == driver_number,
            )
        )
        return self.session.exec(statement).first()

    def upsert_drivers_and_links(self, session_key: int, all_drivers_data: list[dict]):
        new_drivers = 0
        acronyms_from_api = {
            d['name_acronym'] for d in all_drivers_data if d.get('name_acronym')
        }

        existing_drivers_query = self.session.exec(
            select(Driver).where(Driver.name_acronym.in_(acronyms_from_api))
        )
        acronym_driver_map = {driver.name_acronym: driver for driver in existing_drivers_query}

        existing_links_query = self.session.exec(
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
                    self.session.add(driver)
            else:
                driver = Driver(
                    first_name=driver_data.get('first_name', ""),
                    last_name=driver_data.get('last_name', ""),
                    name_acronym=acronym,
                    headshot_url=driver_data.get('headshot_url', ""),
                )
                self.session.add(driver)
                new_drivers += 1
                acronym_driver_map[acronym] = driver
        self.session.flush()

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
                    driver_number=driver_data.get('driver_number'),
                )
                self.session.add(new_session_driver)
                linked += 1
                seen_driver_ids.add(driver.id)
        if new_drivers or linked:
            logger.info(f"  Drivers: {new_drivers} new, {linked} linked to session")


DriverRepoDep = Annotated[DriverRepository, Depends()]
