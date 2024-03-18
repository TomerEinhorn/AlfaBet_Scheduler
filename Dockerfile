FROM python:3.12

# Install Poetry
RUN pip install poetry

WORKDIR /app

# Copy only the poetry files to install dependencies
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . /app

# Run tests
RUN poetry run pytest


# Start the FastAPI server
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
