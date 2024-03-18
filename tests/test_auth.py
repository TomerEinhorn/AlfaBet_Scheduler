from datetime import datetime

import jwt
import os
import sys
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import auth


@patch('app.auth.jwt.encode')
def test_create_access_token_for_user(mock_jwt_encode):
    mock_user = MagicMock()
    token = auth.create_access_token_for_user(mock_user)
    assert token is not None


def test_verify_password():
    hashed_password = auth.get_password_hash("password")
    assert auth.verify_password("password", hashed_password)
    assert not auth.verify_password("wrong_password", hashed_password)


def test_get_user():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_db.query().filter().first.return_value = mock_user
    assert auth.get_user(mock_db, "test_user") == mock_user
    mock_db.query().filter().first.return_value = None
    assert auth.get_user(mock_db, "nonexistent_user") is None


def test_create_access_token():
    data = {"sub": "test_user"}
    token = auth.create_access_token(data)
    assert isinstance(token, str)


def test_get_password_hash():
    password = "password"
    hashed_password = auth.get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0


def test_authenticate_user():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.password_hash = auth.get_password_hash("password")
    mock_db.query().filter().first.return_value = mock_user

    # Correct username and password
    assert auth.authenticate_user("test_user", "password", mock_db) == mock_user

    # Incorrect username or password
    assert not auth.authenticate_user("test_user", "wrong_password", mock_db)
    mock_db.query().filter().first.return_value = None
    assert not auth.authenticate_user("nonexistent_user", "password", mock_db)


@patch('app.auth.jwt.decode')
def test_get_user_name_from_token(mock_jwt_decode):
    mock_jwt_decode.return_value = {"sub": "test_user", "exp": datetime.now().timestamp() + 3600}
    assert auth.get_user_name_from_token("valid_token") == "test_user"

