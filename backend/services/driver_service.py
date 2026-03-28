from typing import Annotated

from fastapi import Depends

from backend.repositories.driver import DriverRepoDep
from backend.schemas.read_driver import DriverResponse


class DriverService:
    def __init__(self, repo: DriverRepoDep):
        self.repo = repo

    def get_drivers(self, session_key: int) -> list[DriverResponse]:
        results = self.repo.get_drivers_from_session_key(session_key)
        return [
            DriverResponse(
                driver_number=session_link.driver_number,
                team=session_link.team,
                first_name=driver.first_name,
                last_name=driver.last_name,
                name_acronym=driver.name_acronym,
                headshot_url=driver.headshot_url,
            )
            for driver, session_link in results
        ]


DriverServiceDep = Annotated[DriverService, Depends()]
