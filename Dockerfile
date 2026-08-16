# ThreatLens backend image.
# Trains the ML model at build time so the image is self-contained --
# no separate training step is needed before the container can serve
# requests. Swap ml/data/raw/urls.csv for a real dataset before
# building a production image (see ml/scripts/generate_dataset.py).
FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2 (PostgreSQL driver) build/runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY ml/ ./ml/

# Train the phishing-detection model so ml/models/model.joblib exists
# before the app starts (ThreatModel refuses to serve without it).
RUN python ml/scripts/generate_dataset.py \
    && python ml/scripts/preprocess.py \
    && python ml/scripts/train.py

WORKDIR /app/backend
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]