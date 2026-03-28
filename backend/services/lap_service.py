from typing import Annotated

from fastapi import Depends

from backend.repositories.driver import DriverRepoDep
from backend.repositories.lap import LapRepoDep
from backend.constants import FALLBACK_COMPOUND
from backend.schemas.driver_laps_schema import DriverLapsResponse, LapResponse


class LapService:
    def __init__(self, driver_repo: DriverRepoDep, lap_repo: LapRepoDep):
        self.driver_repo = driver_repo
        self.lap_repo = lap_repo

    def get_driver_laps(
        self, session_key: int, driver_number: int
    ) -> DriverLapsResponse | None:
        result = self.driver_repo.get_single_driver_from_session_key(
            session_key, driver_number
        )
        if not result:
            return None

        driver, session_data = result
        laps = self.lap_repo.get_laps_for_driver(driver.id, session_key)

        return DriverLapsResponse(
            driver_number=session_data.driver_number,
            first_name=driver.first_name,
            last_name=driver.last_name,
            team=session_data.team,
            headshot_url=driver.headshot_url,
            laps=[
                LapResponse(
                    lap_number=lap.lap_number or 0,
                    time=lap.lap_time or 0.0,
                    speed_trap=lap.st_speed or 0,
                    is_pit_out_lap=lap.is_pit_out_lap or False,
                    compound=lap.compound or FALLBACK_COMPOUND,
                )
                for lap in laps
            ],
        )


LapServiceDep = Annotated[LapService, Depends()]
