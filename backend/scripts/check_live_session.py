import os
import sys
from datetime import datetime, timezone
from sqlalchemy import and_ 

from backend.db.database import engine
from backend.logging_config import logger
from backend.ingestion.update_service import update_db
from backend.models.session_calendar import SessionCalendar
from sqlmodel import Session, select

LOCK_FILE_PATH = "/tmp/update_db_live.lock"

if os.path.exists(LOCK_FILE_PATH):
    logger.warning("Lock file exists. Script may already be running. Exiting.")
    sys.exit()

try:
    with open(LOCK_FILE_PATH, "w") as f:
        f.write(str(os.getpid()))

    logger.info("Starting live session check.")
    with Session(engine) as session:
        time_now = datetime.now(timezone.utc)

        query = select(SessionCalendar).where(
            and_(
                SessionCalendar.start <= time_now,
                SessionCalendar.end >= time_now
            )
        )
        live_session = session.exec(query).first()

        if live_session:
            logger.info(f"Live session found: {live_session.summary}. Running update_db().")
            update_db()
        else:
            logger.info("No live session found.")

finally:
    if os.path.exists(LOCK_FILE_PATH):
        os.remove(LOCK_FILE_PATH)
        logger.info("Lockfile removed.")
