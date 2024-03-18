from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
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
    created_by = Column(String, ForeignKey('users.username'), nullable=False)

    subscriptions = relationship("Subscription", back_populates="event")

    __table_args__ = (
        UniqueConstraint('description', 'location', 'scheduled_time', name='uq_event_details'),
    )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    creation_time = Column(DateTime, default=datetime.now)

    subscriptions = relationship("Subscription", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    event = relationship("Event", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")


