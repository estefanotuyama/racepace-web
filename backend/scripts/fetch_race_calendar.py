from datetime import timedelta
from urllib.request import urlopen

from icalendar import Calendar
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, SQLModel

from backend.db.database import engine
from backend.models.session_calendar import SessionCalendar

SQLModel.metadata.create_all(engine)

# Download calendar
url = "https://files-f1.motorsportcalendars.com/f1-calendar_p1_p2_p3_qualifying_sprint_gp.ics"
with urlopen(url) as response:
    data = response.read().decode("utf-8")

calendar = Calendar.from_ical(data)

with Session(engine) as db:
    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.get("SUMMARY")
            start = component.get("DTSTART").dt
            end = component.get("DTEND").dt + timedelta(hours=1)
            location = component.get("LOCATION")

            stmt = (
                insert(SessionCalendar)
                .values(summary=summary, start=start, end=end, location=location)
                .on_conflict_do_nothing(index_elements=["start", "end"])
            )

            db.execute(stmt)
    db.commit()
