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
        driver_info = self.driver_repo.get_single_driver_from_session_key(
            session_key, driver_number
        )
        if not driver_info:
            return None

        laps = self.lap_repo.get_laps_for_driver(driver_info.id, session_key)

        return DriverLapsResponse(
            driver_number=driver_info.driver_number,
            first_name=driver_info.first_name,
            last_name=driver_info.last_name,
            team=driver_info.team,
            headshot_url=driver_info.headshot_url,
            laps=[
                LapResponse(
                    lap_number=lap.lap_number or 0,
                    time=lap.time or 0.0,
                    speed_trap=lap.speed_trap or 0,
                    is_pit_out_lap=lap.is_pit_out_lap or False,
                    compound=lap.compound or FALLBACK_COMPOUND,
                )
                for lap in laps
            ],
        )


LapServiceDep = Annotated[LapService, Depends()]
