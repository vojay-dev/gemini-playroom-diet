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
create table public.scans (
  id uuid not null primary key,
  created_at timestamptz not null default now(),
  child_age int not null,
  image_path text not null,
  status text not null default 'processing',
  results_json jsonb
);

alter table public.scans enable row level security;
```
