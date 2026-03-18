import logging, time, json
from typing import Annotated
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from fastapi import Depends
from sqlalchemy import select, distinct
from sqlmodel import Session
from backend.db.database import engine, get_session
from backend.models.driver import Driver

"""This script has utilities we use to assist database operations."""

logger = logging.getLogger("racepace")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

SessionDep = Annotated[Session, Depends(get_session)]
URL_BASE = "https://api.openf1.org/v1/"
FALLBACK_COMPOUND = "UNKNOWN"

def get_data(url: str, retries: int = 8):
    """
    Fetches data from the OpenF1 API given a request URL.
    OpenF1 API is unstable, so we have a retrying logic in case something fails.
    :param url: URL for which we want to request data.
    :param retries: Number of retries if request fails.
    :return: Data requested, a list of dictionaries.
    """
    for attempt in range(retries):
        try:
            with urlopen(url) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as e:
            if e.code == 404:
                logger.warning(f"HTTP 404: No data at {url}")
                return None
            wait_time = 2 ** (attempt + 1)
            if e.code == 429 or 500 <= e.code < 600:
                logger.warning(f"[Retry {attempt+1}/{retries}] HTTP {e.code}: Waiting {wait_time}s → {url}")
                time.sleep(wait_time)
            else:
                logger.error(f"Non-retryable HTTPError {e.code} on {url}")
                raise

        except URLError as e:
            wait_time = 2 ** (attempt + 1)
            logger.warning(f"[Retry {attempt+1}/{retries}] URLError: {e.reason} → Waiting {wait_time}s → {url}")
            time.sleep(wait_time)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    logger.error(f"❌ Failed after {retries} retries: {url}")
    return None

def get_session_keys():
    """
    Fetches all session keys available in the database.
    :return: Data requested, a list of session keys.
    """
    with Session(engine) as session:
        query = select(distinct(Driver.session_key))
        result = session.execute(query).scalars().all()
        return result

def get_session_laps(session_key):
    """
    Requests all laps in a given session from the OpenF1 API
    :param session_key: Unique F1 session identifier.
    :return: Data requested, a list of dictionaries.
    """
    url = URL_BASE + f'laps?session_key={session_key}'
    data = get_data(url)
    return data

def map_stints_laps(stints: list[dict]):
    """
    Maps a lap number to the compound used in a stint.
    :param stints: A list of dictionary objects containing stint data.
    :return: Dictionary containing the lap-to-compound mapping.
    """
    stints_hashmap = {}
    if not stints:
        return {}
    for stint in stints:
        lap_start = stint.get('lap_start')
        lap_end = stint.get('lap_end')

        if lap_start is not None and lap_end is not None:
            for i in range(lap_start, lap_end + 1):
                stints_hashmap[i] = stint.get('compound') or FALLBACK_COMPOUND
        else:
            logger.warning(
                f"Skipping stint with incomplete data: driver {stint.get('driver_number')}, "
                f"session {stint.get('session_key')}"
            )
            
    return stints_hashmap
