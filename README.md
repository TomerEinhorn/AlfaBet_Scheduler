# AlfaBet Scheduler 

AlfaBet Scheduler is a FastAPI-based scheduling application that allows users to manage events and receive reminders. This README provides an overview of the application's architecture, setup instructions, performance optimizations, and additional notes.

## Architecture

The application is built using the following technologies:

* FastAPI: A modern web framework for building APIs with Python.
* PostgreSQL: A powerful, open-source relational database.
* Alembic: A lightweight database migration tool for SQLAlchemy.
* Pydantic: Data validation and settings management using Python type annotations.
*APScheduler: A Python library for scheduling tasks.

The application follows a typical CRUD (Create, Read, Update, Delete) architecture, with endpoints for managing events and users. It also includes background tasks for sending reminders and notifications.

## Setup Instructions
#### 1. Clone the Repository:

````
git clone https://github.com/TomerEinhorn/AlfaBet_Scheduler.git
````
#### 2. Navigate to the project repository:
````
cd alfabet-scheduler
````
#### 3. Make sure you have Docker Desktop installed:
If you don't, download it from https://docs.docker.com/get-docker/.
### 4. Build the Docker Containers:
````
docker-compose build
````
### 5. Start the application:
````
docker-compose up
````
### 6. Access the API Documentation:
open this link on your browser: http://localhost:8000/docs.

## APP USAGE
1. Open the link http://localhost:8000/docs. The first thing to do is to create a user. Use the `post/users/` endpoint to
create a user by passing a username and password. All other requests require a registered logged-in user to be performed
successfully.
2. Use the `Authorize` Button at the top right of the page to log in. All you have to fill is the username and password, 
and press `Authorize` to be logged in. 
3. Follow the documentation in the page to see how to use each endpoint. Notice that in order to use any endpoint you 
should first click the `Try it out` button, and after you fill in the required parameters and request body, make sure to
press the `Execute` button for the request to be sent.
4. Notifications for event subscribers will be logged in the cmd wherever you have launched the app.

## Additional Notes
* Ensure Docker Desktop is running before starting the application.

