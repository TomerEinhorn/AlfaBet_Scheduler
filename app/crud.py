from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc

from sqlalchemy.orm import Session
from app import models
from app import schemas
from app.models import User
from app.schemas import UserCreate, SortField
from app.auth import create_access_token_for_user, verify_password, get_password_hash


def create_user(db: Session, user_create: UserCreate):
    hashed_password = get_password_hash(user_create.password)
    db_user = User(username=user_create.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_event(db: Session, event: schemas.EventCreate, user_id: int):
    db_event = models.Event(
        description=event.description,
        location=event.location,
        scheduled_time=event.scheduled_time,
        creation_time=datetime.now(),
        popularity=event.popularity,
        created_by=user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_events(db: Session, skip: int = 0, limit: int = 100, sort_field: SortField = SortField.scheduled_time):
    if sort_field == SortField.scheduled_time:
        return db.query(models.Event).order_by(models.Event.scheduled_time).offset(skip).limit(limit).all()
    elif sort_field == SortField.popularity:
        return db.query(models.Event).order_by(models.Event.popularity).offset(skip).limit(limit).all()
    elif sort_field == SortField.creation_time:
        return db.query(models.Event).order_by(models.Event.creation_time).offset(skip).limit(limit).all()
    else:
        return db.query(models.Event).offset(skip).limit(limit).all()


def get_event_by_id(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def update_event(db: Session, event_id: int, event_update: schemas.EventUpdate):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        for key, value in event_update.dict(exclude_unset=True).items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
        return db_event
    return None


def delete_event_by_id(db: Session, event_id: int):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
        return True
    return False


def get_events_by_location(db: Session, location: str):
    return db.query(models.Event).filter(models.Event.location == location).all()


def get_subscribers(db: Session, event_id: int):
    return db.query(models.Subscription).filter(models.Subscription.event_id == event_id).all()


def create_subscription(db: Session, subscription: schemas.SubscriptionBase):
    db_subscription = models.Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def get_subscription(db: Session, event_id: int, user_id: int):
    return (db.query(models.Subscription).
            filter(models.Subscription.event_id == event_id, models.Subscription.user_id == user_id).first())


def delete_subscription(db: Session, subscription: models.Subscription):
    db.delete(subscription)
    db.commit()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
