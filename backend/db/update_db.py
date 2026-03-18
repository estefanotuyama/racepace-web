from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.models.events import Event
from backend.db.database import engine
from backend.db.db_utils import URL_BASE, get_data, logger, map_stints_laps, FALLBACK_COMPOUND
from backend.models.session_laps import SessionLaps
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session
from backend.models.teams import Teams

from sqlalchemy import select, exists
from sqlmodel import Session, distinct, select, desc
from sqlalchemy.dialects.postgresql import insert
from collections import defaultdict
from sqlalchemy import bindparam, text

"""
This is the script that updates the database.
"""

def fetch_latest_session(session: Session) -> F1Session | None:
    """
    Queries the database to find the latest session we have a record of.
    :param session: Database session
    :return: Latest 'F1Session' session
    """
    result = session.exec(
        select(F1Session).order_by(desc(F1Session.date))
    ).first()
    return result

def add_meetings_to_db(session: Session):
    """
    Queries the Event (meeting) from OpenF1 API and adds it to the database.
    :param session: Database session
    :param meeting_key: Unique meeting identifier
    :return: Boolean informing if the meeting was successfully added
    """
    meetings = get_data(f'{URL_BASE}meetings')

    existing_meetings_query = session.exec(select(Event.meeting_key))
    existing_meetings = set(existing_meetings_query.all())

    added = 0
    for meeting in meetings:
        if meeting.get('meeting_key') in existing_meetings:
            continue

        new_meeting = Event(
                    meeting_key=meeting.get('meeting_key'),
                    circuit_key=meeting.get('circuit_key'),
                    location=meeting.get('location'),
                    country_name=meeting.get('country_name'),
                    circuit_name=meeting.get('circuit_short_name'),
                    meeting_official_name=meeting.get('meeting_official_name'),
                    year=meeting.get('year')
                    )

        session.add(new_meeting)
        added += 1
    logger.info(f"Meetings: {added} new, {len(existing_meetings)} existing")

def add_current_meeting(session, meeting_key):
    existing = session.get(Event, meeting_key)

    if existing:
        return

    meeting = get_data(f'{URL_BASE}meetings?meeting_key={meeting_key}')[0]

    if not meeting:
        logger.warning(f"No meeting data for meeting_key={meeting_key}")
        return

    new_meeting = Event(
                    meeting_key=meeting.get('meeting_key'),
                    circuit_key=meeting.get('circuit_key'),
                    location=meeting.get('location'),
                    country_name=meeting.get('country_name'),
                    circuit_name=meeting.get('circuit_short_name'),
                    meeting_official_name=meeting.get('meeting_official_name'),
                    year=meeting.get('year')
                    )

    session.add(new_meeting)
    session.flush()


def add_session_to_db(session:Session, f1session: dict):
    """
    Adds an F1Session to the database.
    :param session: Database Session
    :param f1session: Formula 1 Session (race, practice, qualifying, etc.)
    :return: None if the session is already in the DB.
    """
    existing = session.get(F1Session, f1session['session_key'])
    if existing:
        return
    new_f1session = F1Session(
        location=f1session.get('location'),
        meeting_key=f1session.get('meeting_key'),
        session_key=f1session.get('session_key'),
        session_type=f1session.get('session_type'),
        session_name=f1session.get('session_name'),
        date=f1session.get('date_start')
    )
    session.add(new_f1session)

def add_drivers_and_session_links(session: Session, session_key: int, all_drivers_data: list[dict]):
    """
    Adds drivers to the DB if they don't exist and links them to the session.
    This function NO LONGER fetches data, it just processes a list of driver data.
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
    for driver_data in all_drivers_data:
        acronym = driver_data.get('name_acronym')
        if not acronym:
            continue
        driver = acronym_driver_map.get(acronym)
        driver_data['driver_id'] = driver.id

        if driver.id not in existing_links_set:
            new_session_driver = SessionDriver(
                session_key=session_key,
                driver_id=driver.id,
                team=driver_data.get('team_name'),
                driver_number=driver_data.get('driver_number')
            )
            session.add(new_session_driver)
            linked += 1
    if new_drivers or linked:
        logger.info(f"  Drivers: {new_drivers} new, {linked} linked to session")

def add_all_laps_for_session(session: Session, session_key: int):
    """
    Fetch lap/stint/driver data, ensure drivers are linked, then batch upsert laps.
    Assumes the caller manages transactions (e.g. with session.begin()).
    """
    logger.info(f"  Fetching laps/stints/drivers from API...")

    # fetch remote data
    laps_url = URL_BASE + f'laps?session_key={session_key}'
    all_laps_data = get_data(laps_url) or []

    stints_url = URL_BASE + f"stints?session_key={session_key}"
    all_stints_data = get_data(stints_url) or []

    drivers_url = URL_BASE + f"drivers?session_key={session_key}"
    all_drivers_data = get_data(drivers_url) or []

    # group by driver_number for quick lookup
    laps_by_driver = defaultdict(list)
    for lap in all_laps_data:
        dn = lap.get('driver_number')
        if dn is None:
            continue
        laps_by_driver[dn].append(lap)

    stints_by_driver = defaultdict(list)
    for stint in all_stints_data:
        dn = stint.get('driver_number')
        if dn is None:
            continue
        stints_by_driver[dn].append(stint)

    # ensure drivers/session links exist
    add_drivers_and_session_links(session, session_key, all_drivers_data)

    # fetch existing laps for this session that already have a compound
    rows = session.exec(
        select(SessionLaps.driver_id, SessionLaps.lap_number).where(
            (SessionLaps.session_key == session_key) & (SessionLaps.compound != None)
        )
    ).all()
    existing_laps = {(r[0], r[1]) for r in rows} if rows else set()

    # collect the parameter dicts we want to upsert
    values_to_upsert: list[dict] = []

    for driver_data in all_drivers_data:
        driver_number = driver_data.get('driver_number')
        driver_id = driver_data.get('driver_id')

        if driver_number is None or driver_id is None:
            continue

        driver_laps = laps_by_driver.get(driver_number, [])
        if not driver_laps:
            continue

        stints_hashmap = map_stints_laps(stints_by_driver.get(driver_number, []))

        for lap in driver_laps:
            lap_num = lap.get('lap_number')
            if lap_num is None:
                continue

            if (driver_id, lap_num) in existing_laps:
                continue

            compound = stints_hashmap.get(lap_num, None)

            values_to_upsert.append({
                'driver_id': driver_id,
                'session_key': lap.get('session_key'),
                'lap_number': lap_num,
                'is_pit_out_lap': lap.get('is_pit_out_lap'),
                'lap_time': lap.get('lap_duration', 0.0),
                'st_speed': lap.get('st_speed', 0),
                'compound': compound,
            })

    if not values_to_upsert:
        logger.info(f"  Laps: 0 new")
        return

    stmt = insert(SessionLaps).values(
        driver_id=bindparam('driver_id'),
        session_key=bindparam('session_key'),
        lap_number=bindparam('lap_number'),
        is_pit_out_lap=bindparam('is_pit_out_lap'),
        lap_time=bindparam('lap_time'),
        st_speed=bindparam('st_speed'),
        compound=bindparam('compound'),
    )

    where_clause_expr = (
        SessionLaps.compound.is_distinct_from(stmt.excluded.compound)
        | SessionLaps.lap_time.is_distinct_from(stmt.excluded.lap_time)
        | SessionLaps.st_speed.is_distinct_from(stmt.excluded.st_speed)
        | SessionLaps.is_pit_out_lap.is_distinct_from(stmt.excluded.is_pit_out_lap)
    )

    do_update = stmt.on_conflict_do_update(
        index_elements=['driver_id', 'session_key', 'lap_number'],
        set_={
            'is_pit_out_lap': stmt.excluded.is_pit_out_lap,
            'lap_time': stmt.excluded.lap_time,
            'st_speed': stmt.excluded.st_speed,
            'compound': stmt.excluded.compound,
        },
        where=where_clause_expr
    )

    session.execute(do_update, values_to_upsert)

    logger.info(f"  Laps: {len(values_to_upsert)} upserted")

def add_session_result_to_db(session:Session, session_key:int):
    """
    Queries OpenF1 API for session results and adds it to db.
    :param session: Database session.
    :param session_key: Unique F1 session key identifier
    :return: returns early if exception.
    """
    data = get_data(URL_BASE + f'session_result?session_key={session_key}')
    if not data:
        return

    added = 0

    session_drivers_query = session.exec(
        select(SessionDriver).where(SessionDriver.session_key == session_key)
    )
    
    driver_map = {sd.driver_number: sd.driver_id for sd in session_drivers_query}

    existing_results_query = session.exec(
        select(SessionResult.driver_id).where(SessionResult.session_key == session_key)
    )
    existing_results_set = set(existing_results_query)

    for datapoint in data:
        driver_number = datapoint.get('driver_number')

        driver_id = driver_map.get(driver_number)

        if not driver_id:
            continue

        if driver_id in existing_results_set:
            continue

        sr_entry = SessionResult(
            meeting_key=datapoint.get('meeting_key'),
            session_key=datapoint.get('session_key'),
            driver_id=driver_id,
            position=datapoint.get('position'),
            duration=str(datapoint.get('duration')),
            number_of_laps=datapoint.get('number_of_laps'),
            gap_to_leader=str(datapoint.get('gap_to_leader')),
            dnf=datapoint.get('dnf'),
            dns=datapoint.get('dns'),
            dsq=datapoint.get('dsq')
        )
        session.add(sr_entry)
        added += 1
    logger.info(f"  Results: {added} added")

def add_teams_colors(session:Session, year=None):
    try: 
        teams = session.exec(select(distinct(SessionDriver.team)))
        existing_teams_query = session.exec(select(Teams.name))
        existing_teams = set(existing_teams_query)

        for team in teams:
            if not team:
                continue
            if team in existing_teams:
                continue
            team_fmt = team.replace(' ', '%20')
            data = get_data(URL_BASE + f'drivers?team_name={team_fmt}')[0]
            if not data :
                continue
            team_colour = data.get('team_colour')

            team = Teams(
                name=team,
                color=f'#{team_colour}'
            )
            session.add(team)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error while adding teams to the DB: {e}")

def update_db():
    """
    Controls the flow to update the database, calling all necessary methods.
    """
    logger.info("Starting database update...")
    with Session(engine) as session:
        data_url = ""
        try:
            latest_session = fetch_latest_session(session)

            if latest_session:
                logger.info(f"Latest session in DB: {latest_session.date}")
                data_url = URL_BASE + f'sessions?date_start>={latest_session.date}'
            else:
                logger.info("Empty database — full population")
                data_url = URL_BASE + 'sessions'
                add_meetings_to_db(session)
                add_teams_colors(session)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")

        data = get_data(data_url)
        total = len(data)
        logger.info(f"Found {total} sessions to process")

        for i, f1session in enumerate(data, 1):
            session_key = f1session['session_key']
            session_name = f1session.get('session_name', '?')
            location = f1session.get('location', '?')
            try:
                with session.begin():
                    logger.info(f"[{i}/{total}] {location} — {session_name} (key={session_key})")
                    add_current_meeting(session, f1session['meeting_key'])
                    add_session_to_db(session, f1session)
                    add_all_laps_for_session(session, session_key)
                    add_session_result_to_db(session, session_key)
            except Exception:
                logger.error(f"[{i}/{total}] FAILED session {session_key}", exc_info=True)
                break

        # Backfill: retry sessions that have no lap data yet
        incomplete = session.exec(
            select(F1Session).where(
                ~exists(
                    select(SessionLaps.id).where(
                        SessionLaps.session_key == F1Session.session_key
                    )
                )
            )
        ).all()

        if incomplete:
            logger.info(f"Backfilling {len(incomplete)} sessions with no lap data...")
            for i, f1sess in enumerate(incomplete, 1):
                try:
                    with session.begin():
                        logger.info(f"  [{i}/{len(incomplete)}] {f1sess.location} — {f1sess.session_name} (key={f1sess.session_key})")
                        add_all_laps_for_session(session, f1sess.session_key)
                        add_session_result_to_db(session, f1sess.session_key)
                except Exception:
                    logger.error(f"  [{i}/{len(incomplete)}] FAILED backfill {f1sess.session_key}", exc_info=True)

    logger.info("Database update complete.")

if __name__ == "__main__":
    from .database import create_db_and_tables
    create_db_and_tables(populating=True)
