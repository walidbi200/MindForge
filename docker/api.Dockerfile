FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/apps/api/src

WORKDIR /app/apps/api

RUN pip install --no-cache-dir uv

COPY apps/api/pyproject.toml ./
COPY apps/api/alembic.ini ./
COPY apps/api/alembic ./alembic
COPY apps/api/src ./src
RUN uv pip install --system -e .

EXPOSE 8000

CMD alembic upgrade head && uvicorn --app-dir src ascend.main:app --host 0.0.0.0 --port ${PORT:-8000}
