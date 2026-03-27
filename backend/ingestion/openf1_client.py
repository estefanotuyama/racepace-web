import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from backend.constants import FALLBACK_COMPOUND

logger = logging.getLogger("racepace")

URL_BASE = "https://api.openf1.org/v1/"


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

    logger.error(f"Failed after {retries} retries: {url}")
    return None


def map_stints_laps(stints: list[dict]) -> dict[int, str]:
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


def fetch_all_meetings() -> list[dict]:
    return get_data(f"{URL_BASE}meetings") or []


def fetch_meeting(meeting_key: int) -> dict | None:
    data = get_data(f"{URL_BASE}meetings?meeting_key={meeting_key}")
    if data:
        return data[0]
    return None


def fetch_sessions(date_start: str | None = None) -> list[dict]:
    if date_start:
        url = f"{URL_BASE}sessions?date_start>={date_start}"
    else:
        url = f"{URL_BASE}sessions"
    return get_data(url) or []


def fetch_laps(session_key: int) -> list[dict]:
    return get_data(f"{URL_BASE}laps?session_key={session_key}") or []


def fetch_stints(session_key: int) -> list[dict]:
    return get_data(f"{URL_BASE}stints?session_key={session_key}") or []


def fetch_drivers(session_key: int) -> list[dict]:
    return get_data(f"{URL_BASE}drivers?session_key={session_key}") or []


def fetch_session_result(session_key: int) -> list[dict]:
    return get_data(f"{URL_BASE}session_result?session_key={session_key}") or []


def fetch_team_color(team_name: str) -> str | None:
    team_fmt = team_name.replace(" ", "%20")
    data = get_data(f"{URL_BASE}drivers?team_name={team_fmt}")
    if data:
        colour = data[0].get("team_colour")
        return f"#{colour}" if colour else None
    return None
