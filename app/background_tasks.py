from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import crud, models, schemas, database
from app.database import SessionLocal
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING)


logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def send_reminder(db: Session, time_delta: timedelta):
    upcoming_events = crud.get_upcoming_events(db, time_delta)
    for event in upcoming_events:
        subscribers = crud.get_subscribers(db, event_id=event.id)
        for subscriber in subscribers:
            logger.info(f"Reminder: Event {event.id} is coming up at {event.scheduled_time}.")


@scheduler.scheduled_job('interval', minutes=1)
def check_upcoming_events():
    db = SessionLocal()
    try:
        time_delta = timedelta(minutes=30)
        send_reminder(db, time_delta)
    finally:
        db.close()


