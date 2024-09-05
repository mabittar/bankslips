# temp stage
FROM python:3.11-slim-buster AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install gcc libpq-dev -y && \
    apt-get autoremove --purge -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app

RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade setuptools wheel
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim-buster

ENV KAFKA_BOOTSTRAP_SERVERS="localhost:9093"

EXPOSE 8000
WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt /app

RUN pip install --no-cache /wheels/*

ENV PYTHONPATH=/app

COPY src /app/src/
# COPY db /app/src/db

RUN useradd -ms /bin/bash appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "src.main:app", "--lifespan", "on", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--forwarded-allow-ips", "*" ]