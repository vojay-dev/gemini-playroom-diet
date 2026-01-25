# Playroom Diet - Backend

FastAPI backend that handles image uploads, triggers the Airflow Gemini AI-agent pipeline, and serves results.

## Features

- **Image Upload**: Receives playroom photos, stores in Supabase Storage
- **Cache Detection**: SHA-256 hashing to avoid reprocessing identical images
- **Airflow Integration**: Triggers the multi-agent Dag via the Airflow REST API (_v2_)
- **Polling Endpoint**: Frontend polls for scan status and results
- **Automatic Cleanup**: APScheduler removes old scans and images periodically (configurable)
- **Cleanup Whitelist**: Protect specific scan IDs from automatic deletion (for demo/example scans)
- **Orphan Cleanup**: On startup, removes storage images not referenced by any scan
- **Daily Limits**: Configurable rate limiting to control API costs

## Tech Stack

- Python 3.12 + [uv](https://github.com/astral-sh/uv)
- [FastAPI + Uvicorn](https://fastapi.tiangolo.com/)
- [Supabase](https://supabase.com/) (Postgres + Storage)
- [APScheduler](https://github.com/agronholm/apscheduler) (periodic background cleanup)
- [Pydantic](https://docs.pydantic.dev/latest/) (data validation)

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
AIRFLOW_STATIC_TOKEN=        # optional, to bypass requesting JWT token and work with a pre-defined one
DAILY_SCAN_LIMIT=20          # optional
GET_RATE_LIMIT=30/minute     # optional
POST_RATE_LIMIT=5/minute     # optional
CLEANUP_AGE_DAYS=2           # optional
CLEANUP_INTERVAL_MINUTES=60  # optional
CLEANUP_WHITELIST=           # optional, comma-separated scan IDs to never delete
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

## Database schema

The backend requires the following table schema to be available. Currently, it is connecting to Supabase, but it is compatible with any PostgreSQL database.

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

## Status flow

Once a scan is created, it gets status `processing` and the Airflow Dag is triggered.

The Dag will then process all open scans, setting their status to `in_flight`, and once done, the status will be updated to `done`.

| Status | Description |
|--------|-------------|
| `processing` | Scan created, awaiting Airflow pickup |
| `in_flight` | Claimed by Airflow Dag, being processed |
| `done` | Successfully completed with results |

## Deployment

Deployed to Google Cloud Run. See [DEPLOYMENT.md](../DEPLOYMENT.md) for instructions.
