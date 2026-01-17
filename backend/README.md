# Gemini Playroom Diet - Backend

## Setup

```sh
uv sync
```

Copy `.env.dist` to `.env` and fill out connection details.

## How to run

```sh
uv run uvicorn main:app --reload
```

## Supabase

Create table and enable row level security:

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
