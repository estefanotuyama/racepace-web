from collections import defaultdict

from sqlmodel import Session

from backend.db.database import engine

from backend.ingestion.openf1_client import (
    fetch_all_meetings,
    fetch_meeting,
    fetch_sessions,
    fetch_laps,
    fetch_stints,
    fetch_drivers,
    fetch_session_result,
    fetch_team_color,
    map_stints_laps,
)
from backend.crud.event import (
    get_existing_meeting_keys,
    insert_meeting,
    meeting_exists,
)
from backend.crud.f1session import (
    insert_f1session,
    fetch_latest_f1session,
    get_incomplete_sessions,
)
from backend.crud.driver import upsert_drivers_and_links
from backend.crud.lap import get_existing_laps_with_compound, bulk_upsert_laps
from backend.crud.session_result import insert_session_results
from backend.crud.team import get_all_team_names, get_existing_team_names, insert_team

from backend.logging_config import logger


def _add_all_meetings(session: Session) -> None:
    meetings = fetch_all_meetings()
    existing = get_existing_meeting_keys(session)
    added = 0
    for meeting in meetings:
        if meeting.get("meeting_key") in existing:
            continue
        insert_meeting(session, meeting)
        added += 1
    logger.info(f"Meetings: {added} new, {len(existing)} existing")


def _ensure_meeting(session: Session, meeting_key: int) -> None:
    if meeting_exists(session, meeting_key):
        return
    meeting_data = fetch_meeting(meeting_key)
    if not meeting_data:
        logger.warning(f"No meeting data for meeting_key={meeting_key}")
        return
    insert_meeting(session, meeting_data)
    session.flush()


def _add_all_laps_for_session(session: Session, session_key: int) -> None:
    logger.info("  Fetching laps/stints/drivers from API...")

    all_laps_data = fetch_laps(session_key)
    all_stints_data = fetch_stints(session_key)
    all_drivers_data_raw = fetch_drivers(session_key)

    # Deduplicate drivers by driver_number
    seen_numbers: set[int] = set()
    all_drivers_data: list[dict] = []
    for d in all_drivers_data_raw:
        dn = d.get("driver_number")
        if dn is not None and dn not in seen_numbers:
            seen_numbers.add(dn)
            all_drivers_data.append(d)

    # Group by driver_number
    laps_by_driver: dict[int, list[dict]] = defaultdict(list)
    for lap in all_laps_data:
        dn = lap.get("driver_number")
        if dn is not None:
            laps_by_driver[dn].append(lap)

    stints_by_driver: dict[int, list[dict]] = defaultdict(list)
    for stint in all_stints_data:
        dn = stint.get("driver_number")
        if dn is not None:
            stints_by_driver[dn].append(stint)

    # Ensure drivers and session links exist (mutates all_drivers_data with driver_id)
    upsert_drivers_and_links(session, session_key, all_drivers_data)

    # Fetch existing laps that already have a compound
    existing_laps = get_existing_laps_with_compound(session, session_key)

    # Build upsert map
    upsert_map: dict[tuple, dict] = {}
    for driver_data in all_drivers_data:
        driver_number = driver_data.get("driver_number")
        driver_id = driver_data.get("driver_id")
        if driver_number is None or driver_id is None:
            continue

        driver_laps = laps_by_driver.get(driver_number, [])
        if not driver_laps:
            continue

        stints_hashmap = map_stints_laps(stints_by_driver.get(driver_number, []))

        for lap in driver_laps:
            lap_num = lap.get("lap_number")
            if lap_num is None:
                continue
            if (driver_id, lap_num) in existing_laps:
                continue

            compound = stints_hashmap.get(lap_num, None)
            key = (driver_id, session_key, lap_num)
            upsert_map[key] = {
                "driver_id": driver_id,
                "session_key": lap.get("session_key"),
                "lap_number": lap_num,
                "is_pit_out_lap": lap.get("is_pit_out_lap"),
                "lap_time": lap.get("lap_duration", 0.0),
                "st_speed": lap.get("st_speed", 0),
                "compound": compound,
            }

    count = bulk_upsert_laps(session, list(upsert_map.values()))
    logger.info(f"  Laps: {count} upserted")


def _add_session_result(session: Session, session_key: int) -> None:
    data = fetch_session_result(session_key)
    insert_session_results(session, session_key, data)


def _add_teams_colors(session: Session) -> None:
    try:
        all_teams = get_all_team_names(session)
        existing = get_existing_team_names(session)
        for team_name in all_teams:
            if not team_name or team_name in existing:
                continue
            color = fetch_team_color(team_name)
            if color:
                insert_team(session, team_name, color)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error while adding teams to the DB: {e}")


def update_db() -> None:
    """
    Controls the flow to update the database, calling all necessary methods.
    """
    logger.info("Starting database update...")
    with Session(engine) as session:
        date_start = None
        try:
            latest_session = fetch_latest_f1session(session)

            if latest_session:
                logger.info(f"Latest session in DB: {latest_session.date}")
                date_start = latest_session.date
            else:
                logger.info("Empty database — full population")
                date_start = None
                _add_all_meetings(session)
                _add_teams_colors(session)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")

        data = fetch_sessions(date_start)
        total = len(data)
        logger.info(f"Found {total} sessions to process")

        for i, f1session in enumerate(data, 1):
            session_key = f1session["session_key"]
            session_name = f1session.get("session_name", "?")
            location = f1session.get("location", "?")
            try:
                with session.begin():
                    logger.info(f"[{i}/{total}] {location} — {session_name} (key={session_key})")
                    _ensure_meeting(session, f1session["meeting_key"])
                    insert_f1session(session, f1session)
                    _add_all_laps_for_session(session, session_key)
                    _add_session_result(session, session_key)
            except Exception:
                logger.error(f"[{i}/{total}] FAILED session {session_key}", exc_info=True)
                break

        # Backfill: retry sessions that have no lap data yet
        incomplete = get_incomplete_sessions(session)

        # Close the implicit transaction from the query above so session.begin() works
        session.rollback()

        if incomplete:
            logger.info(f"Backfilling {len(incomplete)} sessions with no lap data...")
            for i, f1sess in enumerate(incomplete, 1):
                try:
                    with session.begin():
                        logger.info(
                            f"  [{i}/{len(incomplete)}] {f1sess.location} — "
                            f"{f1sess.session_name} (key={f1sess.session_key})"
                        )
                        _add_all_laps_for_session(session, f1sess.session_key)
                        _add_session_result(session, f1sess.session_key)
                except Exception:
                    logger.error(
                        f"  [{i}/{len(incomplete)}] FAILED backfill {f1sess.session_key}",
                        exc_info=True,
                    )

    logger.info("Database update complete.")


if __name__ == "__main__":
    from backend.db.database import create_db_and_tables
    create_db_and_tables(populating=True)
