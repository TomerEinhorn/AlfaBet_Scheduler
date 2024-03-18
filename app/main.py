import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app import crud, models, schemas, database, auth
from app.auth import authenticate_user, create_access_token_for_user, oauth2_scheme, \
    create_access_token
from app.database import SessionLocal, engine
from app.database import get_db
from app.schemas import SortField, BatchUpdateRequest, EventUpdate
from app.background_tasks import scheduler

scheduler.start()

time.sleep(2)

models.Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return app.openapi()


# Create a new user
@app.post("/users/", response_model=schemas.User, summary="endpoint to create a new user in the app",
          description="create a user by providing a username and password")
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.create_user(db, user)
    return db_user


@app.post("/token", include_in_schema=False)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/events/", summary="endpoint to create a new event",
          description="create a new event by providing a description of the event, its location, its scheduled time"
                      " and popularity (number of participants)")
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = auth.get_user_name_from_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return crud.create_event(db=db, event=event, username=username)


@app.get("/events/", response_model=List[schemas.Event], summary="endpoint to view all events listed in the DB")
def get_events(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return crud.get_events(db)


@app.get("/event/{id}", response_model=schemas.Event, summary="endpoint to get an event's details",
         description="provide an event's id to get all of it details")
def get_event_by_description(event_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    event = crud.get_event_by_id(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@app.put("/event/{id}", response_model=schemas.Event, summary="endpoint to update an event's details",
         description="provide an event's id to be able to modify its location, description, "
                     "scheduled time and popularity")
def update_event(event_id: int, event_update: schemas.EventUpdate, db: Session = Depends(get_db),
                 token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    db_event = crud.get_event_by_id(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    updated_event = crud.update_event(db, db_event.id, event_update)
    subscribers = crud.get_subscribers(db, event_id=event_id)
    for subscriber in subscribers:
        logger.info(f"Notification: Event {event_id} has been updated!")
    return updated_event


@app.delete("/event/{id}", summary="an endpoint to delete an event",
            description="provide an event's id to delete it from the db")
def delete_event(event_id: int,  db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    subscribers = crud.get_subscribers(db, event_id=event_id)
    for subscriber in subscribers:
        logger.info(f"Notification: Event {event_id} has been canceled!")
        crud.delete_subscription(db, subscribers)
        logger.info(f"Subscription deleted for user: {subscribers.user_id}")
    success = crud.delete_event_by_id(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}


@app.get("/events/location/{location}", response_model=List[schemas.Event],
         summary="List all events in a given location",
         description="provide a location to get all events from that location")
def get_events_by_location(location: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    events = crud.get_events_by_location(db, location)
    return events


@app.get("/events/sort/{sort_field}", response_model=List[schemas.Event],
         summary="get all events, sorted by a parameter of your choice",
         description="choose to sort events by scheduled time, popularity or creation time")
def get_events_sorted(sort_field: SortField, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return crud.get_events(db, sort_field=sort_field)


@app.post("/events/batch_create/", response_model=List[schemas.Event],
          summary="create multiple events in one request",
          description="provide a description, location, scheduled time and popularity for each event to save "
                      "them all in the db")
def batch_create_events(events: List[schemas.EventCreate], db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return [crud.create_event(db=db, event=event, user_id=user_id) for event in events]


@app.put("/events/batch_update/{event_ids}", summary="update multiple events in one request",
         description="provide the id's of the event you want to update (separated by commas),"
                     " and then update their attributes:"
                     "description, scheduled time, location or popularity for each event to save them all"
                     " in the DB")
async def batch_update_events(event_ids: str, event_data: List[schemas.EventUpdate],
                              db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    event_id_list = [int(id_) for id_ in event_ids.split(",")]
    updated_events = []
    for event_id, new_event_data in zip(event_id_list, event_data):
        db_event = crud.get_event_by_id(db, event_id)
        if db_event is None:
            raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
        updated_event = crud.update_event(db, db_event.id, new_event_data)
        subscribers = crud.get_subscribers(db, event_id=event_id)
        for subscriber in subscribers:
            logger.info(f"Notification: Event {event_id} has been updated!")
        updated_events.append(updated_event)
    return {"message": "Events updated successfully"}


@app.delete("/events/batch_delete/{event_ids}", summary="delete multiple events in one request",
            description="provide event ids (separated by commas) to be deleted from the DB")
def batch_delete_events(event_ids: str, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_name_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    event_id_list = [int(id_) for id_ in event_ids.split(",")]
    for event_id in event_id_list:
        if not crud.get_event_by_id(db=db, event_id=event_id):
            raise HTTPException(status_code=404, detail="Event not found")
        subscribers = crud.get_subscribers(db, event_id=event_id)
        for subscriber in subscribers:
            logger.info(f"Notification: Event {event_id} has been canceled!")
        subscriptions = crud.get_subscribers(db, event_id=event_id)
        for subscription in subscriptions:
            crud.delete_subscription(db, subscription)
        crud.delete_event_by_id(db=db, event_id=event_id)
    return {"message": "Events deleted successfully"}


@app.post("/events/{event_id}/subscribe", response_model=schemas.Subscription,
          summary="subscribe to an event to get notifications about it",
          description="provide an event id to subscribe to it and get notified when it is updated or deleted, "
                      "and get notified 30 minutes prior to its scheduled time")
def subscribe_to_event(event_id: int, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    username = auth.get_user_name_from_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    event = crud.get_event_by_id(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    user = crud.get_user_by_username(db, username=username)
    subscription_data = schemas.SubscriptionBase(event_id=event_id, user_id=user.id)
    subscription = crud.create_subscription(db=db, subscription=subscription_data)
    return subscription


@app.delete("/events/{event_id}/unsubscribe", response_model=schemas.Subscription, summary="Unsubscribe from an event",
            description="provide an event id to unsubscribe from it")
def unsubscribe_from_event(event_id: int, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    username = auth.get_user_name_from_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user = crud.get_user_by_username(db, username=username)
    subscription = crud.get_subscription(db, event_id=event_id, user_id=user.id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    crud.delete_subscription(db, subscription)
    return subscription


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)