FROM python:3.12

# Install Poetry
RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --no-dev

COPY . /app

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
