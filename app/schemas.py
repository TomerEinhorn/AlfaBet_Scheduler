from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime

from enum import Enum


class EventBase(BaseModel):
    description: str
    location: str
    scheduled_time: datetime
    popularity: int


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    creation_time: datetime
    popularity: int
    created_by: str

    class Config:
        orm_mode = True


class EventUpdate(BaseModel):
    description: Optional[str] = None
    location: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    popularity: Optional[int] = None


class UserBase(BaseModel):
    username: str


class SortField(str, Enum):
    scheduled_time = "scheduled_time"
    popularity = "popularity"
    creation_time = "creation_time"



class UserCreate(UserBase):
    username: str
    password: str


class User(UserBase):
    id: int
    creation_time: datetime


class Config:
    orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class BatchUpdateRequest(BaseModel):
    event_ids: List[int]
    event_data: List[dict]


