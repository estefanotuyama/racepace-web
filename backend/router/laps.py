from fastapi import APIRouter

from backend.db.database import SessionDep
from backend.schemas.driver_laps_schema import DriverLapsRead, LapRead
from backend.service.lap import get_driver_lap_times

router = APIRouter()


@router.get("/laps/{year}/{round_number}/{session_name}/{driver_abbreviation}", response_model=DriverLapsRead)
def read_driver_session_laps(
    session: SessionDep, year: int, round_number: int, session_name: str, driver_abbreviation: str
):
    driver, laps = get_driver_lap_times(session, year, round_number, session_name, driver_abbreviation)

    if not driver:
        return DriverLapsRead(
            driver_number="",
            abbreviation="",
            first_name="",
            last_name="",
            team_name="",
            team_color="",
            headshot_url="",
            laps=[],
        )

    driver_laps = DriverLapsRead(
        driver_number=driver.driver_number,
        abbreviation=driver.abbreviation,
        first_name=driver.first_name,
        last_name=driver.last_name,
        team_name=driver.team_name,
        team_color=driver.team_color,
        headshot_url=driver.headshot_url,
        laps=[
            LapRead(
                lap_number=lap.lap_number,
                time=lap.lap_time,
                speed_trap=lap.speed_st,
                is_pit_out_lap=lap.pit_out_time is not None,
                compound=lap.compound,
            )
            for lap in laps
        ],
    )
    return driver_laps
