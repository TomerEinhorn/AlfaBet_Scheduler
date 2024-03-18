from datetime import datetime
from typing import List

from pydantic import ValidationError

from app.schemas import (
    EventBase,
    EventCreate,
    Event,
    EventUpdate,
    UserBase,
    SortField,
    UserCreate,
    User,
    Token,
    BatchUpdateRequest,
    SubscriptionBase,
    SubscriptionCreate,
    Subscription,
)


def test_event_base():
    # Valid EventBase instance
    event_data = {
        "description": "Test Event",
        "location": "Test Location",
        "scheduled_time": datetime.now(),
        "popularity": 0,
    }
    event = EventBase(**event_data)
    assert event.dict() == event_data

    # Invalid EventBase instance (missing required field)
    invalid_event_data = {
        "location": "Test Location",
        "scheduled_time": datetime.now(),
        "popularity": 0,
    }
    try:
        EventBase(**invalid_event_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_event_create():
    # Valid EventCreate instance
    event_create_data = {
        "description": "Test Event",
        "location": "Test Location",
        "scheduled_time": datetime.now(),
        "popularity": 0,
    }
    event_create = EventCreate(**event_create_data)
    assert event_create.dict() == event_create_data

    # Invalid EventCreate instance (missing required field)
    invalid_event_create_data = {
        "location": "Test Location",
        "scheduled_time": datetime.now(),
        "popularity": 0,
    }
    try:
        EventCreate(**invalid_event_create_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_event():
    # Valid Event instance
    event_data = {
        "id": 1,
        "description": "Test Event",
        "location": "Test Location",
        "scheduled_time": datetime.now(),
        "creation_time": datetime.now(),
        "popularity": 0,
        "created_by": "testuser",
    }
    event = Event(**event_data)
    assert event.dict() == event_data

    # Invalid Event instance (missing required field)
    invalid_event_data = {
        "id": 1,
        "description": "Test Event",
        "location": "Test Location",
        "scheduled_time": datetime.now(),
        "creation_time": datetime.now(),
        "popularity": 0,
    }
    try:
        Event(**invalid_event_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_event_update():
    # Valid EventUpdate instance
    event_update_data = {
        "description": "Updated Event Description",
        "location": "Updated Event Location",
        "scheduled_time": datetime.now(),
        "popularity": 1,
    }
    event_update = EventUpdate(**event_update_data)
    assert event_update.dict() == event_update_data

    # Invalid EventUpdate instance (all fields are None)
    invalid_event_update_data = {}
    event_update = EventUpdate(**invalid_event_update_data)
    assert event_update.dict() == {"description": None, "location": None, "scheduled_time": None, "popularity": None}


def test_user_base():
    # Valid UserBase instance
    user_base_data = {"username": "testuser"}
    user_base = UserBase(**user_base_data)
    assert user_base.dict() == user_base_data

    # Invalid UserBase instance (missing required field)
    invalid_user_base_data = {}
    try:
        UserBase(**invalid_user_base_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_sort_field():
    # Valid SortField instance
    sort_field = SortField.scheduled_time
    assert sort_field == "scheduled_time"

    # Invalid SortField instance
    try:
        sort_field = SortField.invalid_field
    except AttributeError:
        pass
    else:
        assert False, "Invalid enum value should raise an exception"


def test_user_create():
    # Valid UserCreate instance
    user_create_data = {"username": "testuser", "password": "testpassword"}
    user_create = UserCreate(**user_create_data)
    assert user_create.dict() == user_create_data

    # Invalid UserCreate instance (missing required field)
    invalid_user_create_data = {"username": "testuser"}
    try:
        UserCreate(**invalid_user_create_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_user():
    # Valid User instance
    user_data = {"id": 1, "username": "testuser", "creation_time": datetime.now()}
    user = User(**user_data)
    assert user.dict() == user_data

    # Invalid User instance (missing required field)
    invalid_user_data = {"id": 1, "username": "testuser"}
    try:
        User(**invalid_user_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_token():
    # Valid Token instance
    token_data = {"access_token": "test_access_token", "token_type": "bearer"}
    token = Token(**token_data)
    assert token.dict() == token_data

    # Invalid Token instance (missing required field)
    invalid_token_data = {"access_token": "test_access_token"}
    try:
        Token(**invalid_token_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_batch_update_request():
    # Valid BatchUpdateRequest instance
    batch_update_request_data = {
        "event_ids": [1, 2, 3],
        "event_data": [{"description": "Event 1"}, {"description": "Event 2"}],
    }
    batch_update_request = BatchUpdateRequest(**batch_update_request_data)
    assert batch_update_request.dict() == batch_update_request_data

    # Invalid BatchUpdateRequest instance (missing required field)
    invalid_batch_update_request_data = {"event_ids": [1, 2, 3]}
    try:
        BatchUpdateRequest(**invalid_batch_update_request_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_subscription_base():
    # Valid SubscriptionBase instance
    subscription_base_data = {"event_id": 1, "user_id": 1}
    subscription_base = SubscriptionBase(**subscription_base_data)
    assert subscription_base.dict() == subscription_base_data

    # Invalid SubscriptionBase instance (missing required field)
    invalid_subscription_base_data = {"event_id": 1}
    try:
        SubscriptionBase(**invalid_subscription_base_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_subscription_create():
    # Valid SubscriptionCreate instance
    subscription_create_data = {"event_id": 1, "user_id": 1}
    subscription_create = SubscriptionCreate(**subscription_create_data)
    assert subscription_create.dict() == subscription_create_data

    # Invalid SubscriptionCreate instance (missing required field)
    invalid_subscription_create_data = {"event_id": 1}
    try:
        SubscriptionCreate(**invalid_subscription_create_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"


def test_subscription():
    # Valid Subscription instance
    subscription_data = {"id": 1, "event_id": 1, "user_id": 1}
    subscription = Subscription(**subscription_data)
    assert subscription.dict() == subscription_data

    # Invalid Subscription instance (missing required field)
    invalid_subscription_data = {"id": 1, "event_id": 1}
    try:
        Subscription(**invalid_subscription_data)
    except ValidationError:
        pass
    else:
        assert False, "Validation should have failed"

