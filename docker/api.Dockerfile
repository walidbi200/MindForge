FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/apps/api

RUN pip install --no-cache-dir uv

COPY apps/api/pyproject.toml ./
COPY apps/api/src ./src

RUN uv pip install --system -e .

EXPOSE 8000

CMD ["uvicorn", "ascend.main:app", "--host", "0.0.0.0", "--port", "8000"]

