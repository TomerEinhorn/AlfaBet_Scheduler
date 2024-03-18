from datetime import datetime
import pytest

from app.models import Event


def test_create_event():
    # Create a new event
    event = Event(
        description="Test Event",
        location="Test Location",
        scheduled_time=datetime.now(),
        created_by="testuser"
    )

    # Check that the event is created correctly
    assert event.description == "Test Event"
    assert event.location == "Test Location"
    assert event.created_by == "testuser"

