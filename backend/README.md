# Playroom Diet - Backend

FastAPI backend that handles image uploads, triggers the Airflow pipeline, and serves results.

## Features

- **Image Upload**: Receives playroom photos, stores in Supabase Storage
- **Cache Detection**: SHA-256 hashing to avoid reprocessing identical images
- **Airflow Integration**: Triggers the multi-agent DAG via REST API
- **Polling Endpoint**: Frontend polls for scan status and results
- **Automatic Cleanup**: APScheduler removes old scans and images (configurable)
- **Daily Limits**: Configurable rate limiting to control API costs

## Tech Stack

- Python 3.12
- FastAPI + Uvicorn
- Supabase (Postgres + Storage)
- APScheduler (background cleanup)
- Pydantic (data validation)

## Setup

```sh
uv sync
```

Copy `.env.dist` to `.env` and configure:

```
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_key
AIRFLOW_HOST=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
CLEANUP_AGE_DAYS=2           # optional
CLEANUP_INTERVAL_MINUTES=60  # optional
DAILY_LIMIT=50               # optional
```

## Running Locally

```sh
uv run uvicorn main:app --reload
```

API runs at `http://localhost:8000`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/scan` | Upload image, returns `scan_id` |
| GET | `/api/scan/{id}` | Get scan status and results |
| GET | `/api/limits` | Get daily usage limits |

## Database Schema (Supabase)

```sql
CREATE TABLE scans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  child_age INTEGER NOT NULL,
  image_path TEXT NOT NULL,
  image_hash VARCHAR(64),
  status VARCHAR(20) NOT NULL DEFAULT 'processing',
  results_json JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.scans ENABLE ROW LEVEL SECURITY;
```

## Deployment

Deployed to Google Cloud Run. See `DEPLOYMENT.md` in root directory for instructions.
