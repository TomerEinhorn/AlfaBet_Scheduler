import logging
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
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

models.Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI()


# TODO: REMOVE THIS FUNCTION BELOW


@app.get("/")
async def read_root():
    return {"message": "AlfaBet Scheduler API is running."}


# Create a new user
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.create_user(db, user)
    return db_user


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# # Authenticate user and return JWT token
# @app.post("/token")
# def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}


@app.post("/events/")
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return crud.create_event(db=db, event=event, user_id=user_id)


@app.get("/events/", response_model=List[schemas.Event])
def get_events(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return crud.get_events(db)


@app.get("/event/{id}", response_model=schemas.Event)
def get_event_by_description(event_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    event = crud.get_event_by_id(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@app.put("/event/{id}", response_model=schemas.Event)
def update_event(event_id: int, event_update: schemas.EventUpdate, db: Session = Depends(get_db),
                 token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    db_event = crud.get_event_by_id(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    updated_event = crud.update_event(db, db_event.id, event_update)
    return updated_event


@app.delete("/event/{id}")
def delete_event(event_id: int,  db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    success = crud.delete_event_by_id(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}


@app.get("/events/location/{location}", response_model=List[schemas.Event])
def get_events_by_location(location: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    events = crud.get_events_by_location(db, location)
    return events


@app.get("/events/sort/{sort_field}", response_model=List[schemas.Event])
def get_events_sorted(sort_field: SortField, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return crud.get_events(db, sort_field=sort_field)


@app.post("/events/batch_create/", response_model=List[schemas.Event])
def batch_create_events(events: List[schemas.EventCreate], db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return [crud.create_event(db=db, event=event, user_id=user_id) for event in events]


@app.put("/events/batch_update/{event_ids}")
async def batch_update_events(event_ids: str, event_data: List[schemas.EventUpdate],
                              db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    event_id_list = [int(id_) for id_ in event_ids.split(",")]
    updated_events = []
    for event_id, new_event_data in zip(event_id_list, event_data):
        db_event = crud.get_event_by_id(db, event_id)
        if db_event is None:
            raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
        updated_event = crud.update_event(db, db_event.id, new_event_data)
        updated_events.append(updated_event)
    return {"message": "Events updated successfully"}


@app.delete("/events/batch_delete/{event_ids}")
def batch_delete_events(event_ids: str, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    user_id = auth.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    event_id_list = [int(id_) for id_ in event_ids.split(",")]
    for event_id in event_id_list:
        if not crud.get_event_by_id(db=db, event_id=event_id):
            raise HTTPException(status_code=404, detail="Event not found")
        crud.delete_event_by_id(db=db, event_id=event_id)
    return {"message": "Events deleted successfully"}


# Implement other endpoints...


