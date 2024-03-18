from datetime import timedelta
from unittest.mock import MagicMock, patch

from app import background_tasks


@patch('app.background_tasks.crud.get_upcoming_events')
@patch('app.background_tasks.crud.get_subscribers')
def test_send_reminder(mock_get_subscribers, mock_get_upcoming_events):
    mock_db = MagicMock()
    mock_event = MagicMock()
    mock_subscriber = MagicMock()

    mock_get_upcoming_events.return_value = [mock_event]
    mock_get_subscribers.return_value = [mock_subscriber]

    background_tasks.send_reminder(mock_db, timedelta(minutes=30))

    mock_get_upcoming_events.assert_called_once_with(mock_db, timedelta(minutes=30))
    mock_get_subscribers.assert_called_once_with(mock_db, event_id=mock_event.id)


@patch('app.background_tasks.SessionLocal')
@patch('app.background_tasks.send_reminder')
def test_check_upcoming_events(mock_send_reminder, mock_SessionLocal):
    mock_db = MagicMock()
    mock_SessionLocal.return_value = mock_db

    background_tasks.check_upcoming_events()

    mock_SessionLocal.assert_called_once()
    mock_send_reminder.assert_called_once_with(mock_db, timedelta(minutes=30))
