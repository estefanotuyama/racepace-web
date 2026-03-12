"""
FastF1-based ingestion script.

Usage:
    python -m backend.db.ingest
    python -m backend.db.ingest --year 2024
    python -m backend.db.ingest --year 2024 --round 1
"""

import argparse
import logging
import time
from datetime import datetime

import fastf1
import pandas as pd
from sqlmodel import Session

from backend.db.database import create_db_and_tables, engine
from backend.models.driver import Driver
from backend.models.events import Event
from backend.models.session_laps import SessionLaps
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session
from backend.models.teams import Teams
from backend.repository import (
    driver_repo,
    event_repo,
    lap_repo,
    result_repo,
    session_repo,
    team_repo,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Quiet down FastF1's verbose logging
#logging.getLogger("fastf1").setLevel(logging.WARNING)
#logging.getLogger("urllib3").setLevel(logging.WARNING)

fastf1.Cache.enable_cache("cache")

YEARS = range(2018, 2027)
SESSION_NAMES = [
    "Practice 1",
    "Practice 2",
    "Practice 3",
    "Sprint Qualifying",
    "Sprint",
    "Qualifying",
    "Race",
]


def td_to_seconds(val) -> float | None:
    """Convert a pandas Timedelta to total seconds, returning None for NaT/NaN."""
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timedelta):
        return val.total_seconds()
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def safe_float(val) -> float | None:
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def safe_str(val, default: str = "") -> str:
    if pd.isna(val):
        return default
    return str(val)


def safe_bool(val, default: bool = False) -> bool:
    if pd.isna(val):
        return default
    return bool(val)


def ingest_session(db: Session, ff1_session, db_event: Event, session_name: str, year: int):
    """Ingest a single F1 session's data."""
    t0 = time.monotonic()
    try:
        ff1_session.load(laps=True, telemetry=False, weather=False, messages=False)
    except Exception as e:
        logger.warning("    [SKIP] %s — could not load: %s", session_name, e)
        return

    # Upsert F1Session
    session_date = ff1_session.date
    if isinstance(session_date, pd.Timestamp):
        session_date = session_date.to_pydatetime()
    if session_date is None or (isinstance(session_date, datetime) and session_date.year < 2000):
        session_date = db_event.event_date

    f1_api_support = bool(getattr(ff1_session, "f1_api_support", False))

    db_session = session_repo.upsert_session(
        db,
        F1Session(
            session_name=session_name,
            date=session_date,
            round_number=db_event.round_number,
            year=year,
            f1_api_support=f1_api_support,
            event_id=db_event.id,
        ),
    )
    db.flush()

    # Process results if available
    driver_count = 0
    results = ff1_session.results
    if results is not None and not results.empty:
        for _, row in results.iterrows():
            abbreviation = safe_str(row.get("Abbreviation"))
            if not abbreviation:
                continue

            driver_number = safe_str(row.get("DriverNumber"))
            first_name = safe_str(row.get("FirstName"))
            last_name = safe_str(row.get("LastName"))
            full_name = safe_str(row.get("FullName"))
            headshot_url = safe_str(row.get("HeadshotUrl"))
            country_code = safe_str(row.get("CountryCode"))
            team_name = safe_str(row.get("TeamName"))
            team_color_raw = safe_str(row.get("TeamColor"))
            team_color = (
                f"#{team_color_raw}" if team_color_raw and not team_color_raw.startswith("#") else team_color_raw
            )

            # Upsert driver
            db_driver = driver_repo.upsert_driver(
                db,
                Driver(
                    driver_number=driver_number,
                    abbreviation=abbreviation,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    headshot_url=headshot_url,
                    country_code=country_code,
                    team_name=team_name,
                    team_color=team_color,
                ),
            )
            db.flush()

            # Upsert team
            if team_name:
                team_repo.upsert_team(db, Teams(name=team_name, color=team_color))

            # Upsert result
            result_repo.upsert_result(
                db,
                SessionResult(
                    session_id=db_session.id,
                    driver_id=db_driver.id,
                    team_name=team_name,
                    team_color=team_color,
                    position=safe_float(row.get("Position")),
                    classified_position=safe_str(row.get("ClassifiedPosition")),
                    grid_position=safe_float(row.get("GridPosition")),
                    q1=td_to_seconds(row.get("Q1")),
                    q2=td_to_seconds(row.get("Q2")),
                    q3=td_to_seconds(row.get("Q3")),
                    time=td_to_seconds(row.get("Time")),
                    status=safe_str(row.get("Status")),
                    points=safe_float(row.get("Points")) or 0.0,
                    laps=safe_float(row.get("Laps")),
                ),
            )
            driver_count += 1

    # Process laps if available
    lap_count = 0
    laps_df = ff1_session.laps
    if laps_df is not None and not laps_df.empty:
        for _, lap_row in laps_df.iterrows():
            abbreviation = safe_str(lap_row.get("Driver"))
            if not abbreviation:
                continue

            db_driver = driver_repo.get_driver_by_abbreviation(db, abbreviation)
            if not db_driver:
                continue

            lap_number = int(lap_row.get("LapNumber", 0))
            if lap_number <= 0:
                continue

            lap_repo.upsert_lap(
                db,
                SessionLaps(
                    session_id=db_session.id,
                    driver_id=db_driver.id,
                    driver_abbreviation=abbreviation,
                    driver_number=db_driver.driver_number,
                    lap_number=lap_number,
                    lap_time=td_to_seconds(lap_row.get("LapTime")),
                    stint=int(safe_float(lap_row.get("Stint")) or 0),
                    pit_out_time=td_to_seconds(lap_row.get("PitOutTime")),
                    pit_in_time=td_to_seconds(lap_row.get("PitInTime")),
                    sector1_time=td_to_seconds(lap_row.get("Sector1Time")),
                    sector2_time=td_to_seconds(lap_row.get("Sector2Time")),
                    sector3_time=td_to_seconds(lap_row.get("Sector3Time")),
                    speed_i1=safe_float(lap_row.get("SpeedI1")),
                    speed_i2=safe_float(lap_row.get("SpeedI2")),
                    speed_fl=safe_float(lap_row.get("SpeedFL")),
                    speed_st=safe_float(lap_row.get("SpeedST")),
                    is_personal_best=safe_bool(lap_row.get("IsPersonalBest")),
                    compound=safe_str(lap_row.get("Compound")) or None,
                    tyre_life=safe_float(lap_row.get("TyreLife")),
                    fresh_tyre=safe_bool(lap_row.get("FreshTyre")) if not pd.isna(lap_row.get("FreshTyre")) else None,
                    track_status=safe_str(lap_row.get("TrackStatus")),
                    position=safe_float(lap_row.get("Position")),
                    deleted=safe_bool(lap_row.get("Deleted")) if not pd.isna(lap_row.get("Deleted")) else None,
                    is_accurate=safe_bool(lap_row.get("IsAccurate"), default=True),
                ),
            )
            lap_count += 1

    db.commit()
    elapsed = time.monotonic() - t0
    logger.info("    %-20s %d drivers, %d laps (%.1fs)", session_name, driver_count, lap_count, elapsed)


def ingest_event(db: Session, event_row, year: int):
    """Ingest a single event and all its sessions."""
    round_number = int(event_row["RoundNumber"])
    if round_number == 0:
        return

    event_date = event_row.get("EventDate")
    if isinstance(event_date, pd.Timestamp):
        event_date = event_date.to_pydatetime()

    event_name = safe_str(event_row.get("EventName"))

    db_event = event_repo.upsert_event(
        db,
        Event(
            round_number=round_number,
            country=safe_str(event_row.get("Country")),
            location=safe_str(event_row.get("Location")),
            official_event_name=safe_str(event_row.get("OfficialEventName")),
            event_name=event_name,
            event_date=event_date,
            event_format=safe_str(event_row.get("EventFormat")),
            year=year,
        ),
    )
    db.flush()

    logger.info("  Round %d — %s", round_number, event_name)

    for session_name in SESSION_NAMES:
        try:
            ff1_session = fastf1.get_session(year, round_number, session_name)
        except Exception:
            continue
        ingest_session(db, ff1_session, db_event, session_name, year)


def ingest_all(years=None):
    """Ingest all events for the given years."""
    if years is None:
        years = YEARS

    create_db_and_tables()
    total_start = time.monotonic()

    for year in years:
        year_start = time.monotonic()
        logger.info("=== %d ===", year)
        try:
            schedule = fastf1.get_event_schedule(year)
        except Exception as e:
            logger.warning("Could not get schedule for %d: %s", year, e)
            continue

        num_events = len(schedule[schedule["RoundNumber"] > 0])
        logger.info("Found %d events for %d", num_events, year)

        with Session(engine) as db:
            for _, event_row in schedule.iterrows():
                try:
                    ingest_event(db, event_row, year)
                except Exception as e:
                    logger.error("Error ingesting round %s: %s", event_row.get("RoundNumber", "?"), e)
                    db.rollback()
                    continue

        year_elapsed = time.monotonic() - year_start
        logger.info("=== %d complete (%.0fs) ===", year, year_elapsed)

    total_elapsed = time.monotonic() - total_start
    logger.info("Ingestion finished — %d year(s) in %.0fs", len(list(years)), total_elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest F1 data via FastF1")
    parser.add_argument("--year", type=int, help="Single year to ingest")
    parser.add_argument("--round", type=int, help="Single round to ingest (requires --year)")
    args = parser.parse_args()

    if args.year and args.round:
        logger.info("Ingesting %d Round %d", args.year, args.round)
        create_db_and_tables()
        t0 = time.monotonic()
        with Session(engine) as db:
            ff1_schedule = fastf1.get_event_schedule(args.year)
            event_row = ff1_schedule[ff1_schedule["RoundNumber"] == args.round].iloc[0]
            ingest_event(db, event_row, args.year)
        logger.info("Done in %.0fs", time.monotonic() - t0)
    elif args.year:
        ingest_all(years=[args.year])
    else:
        ingest_all()
