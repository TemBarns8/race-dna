FROM python:3.14.6-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

COPY backend/pyproject.toml /app/backend/pyproject.toml
COPY backend/src /app/backend/src

RUN python -m pip install --no-cache-dir /app/backend

COPY alembic.ini /app/alembic.ini
COPY backend/alembic /app/backend/alembic

USER app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "race_dna.main:app", "--host", "0.0.0.0", "--port", "8000"]