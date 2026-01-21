# Playroom Diet - Airflow

Multi-agent AI pipeline for playroom analysis using Apache Airflow 3.0 and Gemini 3 Flash.

## Overview

This DAG (`process_scans`) orchestrates 4 AI agents that transform a playroom photo into a personalized child development plan. Each agent has a focused task with structured Pydantic outputs.

## Pipeline Architecture

```
┌─────────────────┐
│  get_new_scans  │ ← SQL query for pending scans
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
- **Model**: Gemini 3 Flash (Vision)
- **Input**: Playroom photo from Supabase Storage
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
- Apache Airflow 3.0+ with AI SDK (`airflow-ai-sdk`)
- Astronomer CLI (recommended) or standalone Airflow

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
- DAG Processor
- API Server
- Triggerer

Access Airflow UI at `http://localhost:8080`

## Triggering the DAG

The backend triggers the DAG via REST API when a new scan is uploaded:
```
POST /api/v1/dags/process_scans/dagRuns
```

The DAG polls for scans with `status = 'processing'` and processes them.

## Key Technical Details

- **Dynamic Task Mapping**: Uses `.expand()` to process multiple scans in parallel
- **Structured Outputs**: `@task.llm` decorator with `output_type` ensures schema compliance
- **Resolution-Independent**: Bounding boxes use normalized 0-1 coordinates
- **Parallel Execution**: Play Quest generation runs alongside the analysis branch
