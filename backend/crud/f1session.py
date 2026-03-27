from sqlalchemy import exists as sa_exists
from sqlmodel import Session, select, desc
from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.models.session_laps import SessionLaps
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session
from backend.schemas.read_session_result import DriverPosition, ReadSessionResult


def get_sessions_from_meeting_key(session:Session, meeting_key:int):
    """
    Queries the db for all F1 sessions in an F1 event.
    :param session: Database session, not related to an F1 session.
    :param meeting_key: Unique key identifying an event.
    :return: List of sessions as 'F1Session' pydantic model.
    """
    return session.exec(select(F1Session).where(F1Session.meeting_key == meeting_key)).all()


def get_session_result(session: Session, session_key: int):
    """
    Gets all results for a session, joining the result, driver, and session link data,
    ordered by finishing position.
    """
    statement = (
        # 1. State what you want to select in the final result.
        select(SessionResult, Driver, SessionDriver)
        # 2. Explicitly state the starting table for your joins.
        .select_from(SessionResult)
        # 3. Create a clear, sequential join path: SessionResult -> Driver
        .join(Driver, SessionResult.driver_id == Driver.id)
        # 4. Continue the path: Driver -> SessionDriver
        .join(SessionDriver, Driver.id == SessionDriver.driver_id)
        # 5. Now filter the query. Add all necessary conditions.
        .where(SessionResult.session_key == session_key)
        .where(SessionDriver.session_key == session_key)
        # 6. Order the final results.
        .order_by(SessionResult.position)
    )

    result = session.exec(statement).all()

    driver_positions = [
        DriverPosition(
            position=result.position,
            team=session_link.team,
            first_name=driver.first_name,
            last_name=driver.last_name,
            number_of_laps=result.number_of_laps,
            gap_to_leader=result.gap_to_leader,
            duration=result.duration,
            dnf=result.dnf,
            dns=result.dns,
            dsq=result.dsq
        )
        for result, driver, session_link in result
    ]

    session_table= ReadSessionResult(
        result=driver_positions
    )

    return session_table


def fetch_latest_f1session(session: Session) -> F1Session | None:
    return session.exec(
        select(F1Session).order_by(desc(F1Session.date))
    ).first()


def insert_f1session(session: Session, f1session_data: dict) -> None:
    existing = session.get(F1Session, f1session_data["session_key"])
    if existing:
        return
    new_f1session = F1Session(
        location=f1session_data.get("location"),
        meeting_key=f1session_data.get("meeting_key"),
        session_key=f1session_data.get("session_key"),
        session_type=f1session_data.get("session_type"),
        session_name=f1session_data.get("session_name"),
        date=f1session_data.get("date_start"),
    )
    session.add(new_f1session)


def get_incomplete_sessions(session: Session) -> list[F1Session]:
    return session.exec(
        select(F1Session).where(
            ~sa_exists(
                select(SessionLaps.id).where(
                    SessionLaps.session_key == F1Session.session_key
                )
            )
        )
    ).all()
