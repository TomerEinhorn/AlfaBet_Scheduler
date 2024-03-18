from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from app import crud, models, schemas


def test_create_user():
    db_mock = MagicMock(spec=Session)
    user_create = schemas.UserCreate(username="testuser", password="testpassword")

    user = crud.create_user(db_mock, user_create)

    assert user.username == user_create.username


def test_create_event():
    db_mock = MagicMock(spec=Session)
    event_create = schemas.EventCreate(
        description="Test Event",
        location="Test Location",
        scheduled_time=datetime.now(),
        popularity=1
    )
    user_id = 1

    event = crud.create_event(db_mock, event_create, user_id)

    assert event.description == event_create.description


def test_get_events():
    db_mock = MagicMock(spec=Session)

    events = crud.get_events(db_mock)

    assert events is not None


def test_get_event_by_id():
    db_mock = MagicMock(spec=Session)
    event_id = 1

    event = crud.get_event_by_id(db_mock, event_id)

    assert event is not None


def test_update_event():
    db_mock = MagicMock(spec=Session)
    event_id = 1
    event_update = schemas.EventUpdate(description="Updated Description")

    updated_event = crud.update_event(db_mock, event_id, event_update)

    assert updated_event is not None


def test_delete_event_by_id():
    db_mock = MagicMock(spec=Session)
    event_id = 1

    result = crud.delete_event_by_id(db_mock, event_id)

    assert result is True


def test_get_events_by_location():
    db_mock = MagicMock(spec=Session)
    location = "Test Location"

    events = crud.get_events_by_location(db_mock, location)

    assert events is not None


def test_get_subscribers():
    db_mock = MagicMock(spec=Session)
    event_id = 1

    subscribers = crud.get_subscribers(db_mock, event_id)

    assert subscribers is not None


def test_create_subscription():
    db_mock = MagicMock(spec=Session)
    subscription = schemas.SubscriptionBase(event_id=1, user_id=1)

    created_subscription = crud.create_subscription(db_mock, subscription)

    assert created_subscription is not None


def test_get_subscription():
    db_mock = MagicMock(spec=Session)
    event_id = 1
    user_id = 1

    subscription = crud.get_subscription(db_mock, event_id, user_id)

    assert subscription is not None


def test_delete_subscription():
    db_mock = MagicMock(spec=Session)
    subscription = models.Subscription(event_id=1, user_id=1)

    crud.delete_subscription(db_mock, subscription)

    assert True  # No  needed, just checking for no exceptions


def test_get_user_by_username():
    db_mock = MagicMock(spec=Session)
    username = "testuser"

    user = crud.get_user_by_username(db_mock, username)

    assert user is not None


def test_get_upcoming_events():
    now = datetime.now()
    db_mock = MagicMock(spec=Session)
    time_delta = timedelta(days=1)
    end_time = now + time_delta

    events = crud.get_upcoming_events(db_mock, time_delta)

    assert events is not None
