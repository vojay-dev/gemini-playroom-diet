# Playroom Diet - Airflow

Multi-agent AI pipeline for playroom analysis using [Apache Airflow 3.1](https://airflow.apache.org/), the [Airflow AI SDK](https://github.com/astronomer/airflow-ai-sdk) and Gemini 3 Flash.

## Overview

This Airflow project contains one Dag (`process_scans`), which orchestrates 4 AI agents that transform a playroom photo into a personalized child development plan. Each agent has a focused task with structured Pydantic outputs.

The Dag has no `schedule` and is meant to be triggered via the Airflow REST API by the Playroom Diet backend every time a playroom picture is uploaded.

Once started, it will claim pending scans from the underlying Postgres `scans` table using atomic locking. All agent tasks use dynamic task mapping to process scans in parallel, with runtime generated tasks (one per scan). To ensure system stability, the parallelism per task is limited via `max_active_tis_per_dag`.

### Race Condition Handling

The Dag uses **atomic scan claiming** via `UPDATE ... FOR UPDATE SKIP LOCKED` to prevent race conditions:

1. When `get_new_scans` runs, it atomically claims up to 10 scans by setting their status from `processing` to `in_flight`
2. The `FOR UPDATE SKIP LOCKED` clause ensures concurrent Dag runs claim different scans
3. Multiple Dag runs can process in parallel, each working on its own set of scans
4. This eliminates wait times compared to the previous `max_active_runs=1` approach

**Status flow**: `processing` (new) -> `in_flight` (claimed) -> `done` (complete)

## Pipeline Architecture

```
┌─────────────────┐
│  get_new_scans  │ ← Atomic claim: UPDATE ... FOR UPDATE SKIP LOCKED
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  analyze_image  │ ← Agent 1: Vision AI extracts toy inventory
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌─────────────────────┐
│ quest  │  │  analyze_playroom   │ ← Agent 2: O*NET skill mapping
└───┬────┘  └──────────┬──────────┘
    │                  │
    │                  ▼
    │       ┌─────────────────┐
    │       │  safety_check   │ ← Agent 3: CPSC safety audit
    │       └────────┬────────┘
    │                │
    └────────┬───────┘
             ▼
      ┌─────────────┐
      │ save_result │ → Updates Supabase with results
      └─────────────┘
```

## AI Agents

### Agent 1: `analyze_image`
- **Model**: Gemini 3 Flash (vision)
- **Input**: Playroom photo from the image storage
- **Output**: `ToyInventory` with bounding boxes
- **Purpose**: Extract every visible toy with normalized coordinates (0-1 range)

### Agent 2: `analyze_playroom`
- **Model**: Gemini 3 Flash
- **Input**: Toy inventory + child's age
- **Output**: `AnalysisResult` with skill scores and 3-item roadmap
- **Purpose**: Map toys to O*NET abilities, score 6 development categories, identify gaps

### Agent 3: `safety_check`
- **Model**: Gemini 3 Flash
- **Input**: Development roadmap + child's age
- **Output**: `ToyRecommendation` with safety decisions
- **Purpose**: Validate against CPSC guidelines, substitute unsafe toys, generate shopping queries

### Agent 4: `generate_play_quest`
- **Model**: Gemini 3 Flash
- **Input**: Toy inventory + child's age
- **Output**: `PlayQuest` activity details
- **Purpose**: Create an immediate play activity using existing toys
- **Note**: Runs in parallel with Agent 2

## Pydantic Models

All LLM outputs use strict Pydantic schemas:

```python
ToyInventory      # List of toys with bounding boxes
AnalysisResult    # Status quo, skill scores, roadmap
ToyRecommendation # Safety-checked recommendations
PlayQuest         # Structured play activity
```

## Setup

### Prerequisites

- Astro CLI

### Environment Variables
```
SUPABASE_PROJECT_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_key
```

### Airflow Connection
Create a Postgres connection with ID `postgres_playroom_diet` pointing to your Supabase database.

## Running Locally

Using Astronomer CLI:
```sh
astro dev start
```

This starts:
- Postgres (metadata DB)
- Scheduler
- Dag Processor
- API Server
- Triggerer

Access Airflow UI at `http://localhost:8080`

## Triggering the Dag

The backend triggers the Dag via REST API when a new scan is uploaded:
```
POST /api/v1/dags/process_scans/dagRuns
```

The Dag polls for scans with `status = 'processing'` and processes them.

## Key Technical Details

- **Atomic Claiming**: Uses `UPDATE ... FOR UPDATE SKIP LOCKED` to prevent race conditions between concurrent Dag runs
- **Dynamic Task Mapping**: Uses `.expand()` to process multiple scans in parallel
- **Structured Outputs**: `@task.llm` decorator with `output_type` ensures schema compliance
- **Resolution-Independent**: Bounding boxes use normalized 0-1 coordinates
- **Parallel Execution**: Play Quest generation runs alongside the analysis branch
