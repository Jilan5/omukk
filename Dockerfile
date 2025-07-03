FROM python:3.12-slim

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/ufoscout/docker-compose-wait:latest /wait /wait

WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to not create virtual environment in container
RUN poetry config virtualenvs.create false

# Copy poetry files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --only main --no-root --no-directory

COPY . /app
RUN poetry install --only main

EXPOSE 8000

CMD /wait; poetry run alembic upgrade head; poetry run fastapi run
