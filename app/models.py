from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy.orm import relationship

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    creation_time = Column(DateTime, default=datetime.now)
    popularity = Column(Integer, default=0)
    created_by = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    creation_time = Column(DateTime, default=datetime.now)


