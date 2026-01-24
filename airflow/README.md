# Playroom Diet - Airflow

Multi-agent AI pipeline for playroom analysis using [Apache Airflow 3.1](https://airflow.apache.org/), the [Airflow AI SDK](https://github.com/astronomer/airflow-ai-sdk) and Gemini 3 Flash.

## Overview

This Airflow project contains one Dag (`process_scans`), which orchestrates 4 AI agents that transform a playroom photo into a personalized child development plan. Each agent has a focused task with structured Pydantic outputs.

The Dag has no `schedule` and is meant to be triggered via the Airflow REST API by the Playroom Diet backend every time a playroom picture is uploaded.

Once started, it will claim pending scans from the underlying Postgres `scans` table using atomic locking. All agent tasks use dynamic task mapping to process scans in parallel, with runtime generated tasks (one per scan). To ensure system stability, the parallelism per task is limited via `max_active_tis_per_dag` and the overall Dag parallelism is limited via `max_active_runs`.

### Race condition handling

The Dag uses **atomic scan claiming** via `UPDATE ... FOR UPDATE SKIP LOCKED` to prevent race conditions:

1. When `get_new_scans` runs, it atomically claims open scans by setting their status from `processing` to `in_flight` in one atomic operation.
2. The `FOR UPDATE SKIP LOCKED` clause ensures concurrent Dag runs claim different scans.
3. Multiple Dag runs can process in parallel, each working on its own set of scans.
4. This eliminates wait times in case a user submits a playroom picture while the Dag is running.

**Status flow**: `processing` (new) -> `in_flight` (claimed) -> `done` (complete)

## Pipeline architecture

```
┌─────────────────┐
│  get_new_scans  │ ← Atomic claim of open scans
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
│ quest  │  │  analyze_playroom   │ ← Agent 2: O*NET skill mapping and toy analysis
└───┬────┘  └──────────┬──────────┘ ← Agent 3: Focus on existing toys to generate a play quest
    │                  │
    │                  ▼
    │       ┌─────────────────┐
    │       │  safety_check   │ ← Agent 4: CPSC safety audit
    │       └────────┬────────┘
    │                │
    └────────┬───────┘
             ▼
      ┌─────────────┐
      │ save_result │ → Updates Supabase with results
      └─────────────┘
```

## AI agents and the Airflow AI SDK

The [Airflow AI SDK](https://github.com/astronomer/airflow-ai-sdk) is an open-source Python library, that facilitates the integration and orchestration of LLMs and AI agents directly within Apache Airflow pipelines. It provides decorator-based tasks to seamlessly incorporate AI functionality into traditional data and machine learning workflows. It is based on [PydanticAI](https://ai.pydantic.dev/) so that many of the features can be used.

The model used for all agents is `gemini-3-flash-preview`.

For Playroom Diet, all agents are defined with a model, a strict Pydantic output type, a system prompt based on the role in the multi-agent system, and some are provided with tool functions.

**Example:**

```python
@task.agent(
    agent=Agent(
        model="gemini-3-flash-preview",
        output_type=AnalysisResult,
        system_prompt="...",
        tools=[duckduckgo_search_tool()]
    )
)
```

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

## Pydantic models

All agent outputs use strict Pydantic schemas:

```python
ToyInventory      # List of toys with bounding boxes
AnalysisResult    # Status quo, skill scores, roadmap
ToyRecommendation # Safety-checked recommendations
PlayQuest         # Structured play activity
```

## Setup

### Prerequisites

- [Astro CLI](https://github.com/astronomer/astro-cli)

### Environment variables

Copy `.env.dist` to `.env` and configure:

```
AIRFLOW_CONN_POSTGRES_PLAYROOM_DIET=postgresql://<supabase_connection_string>?sslmode=require
GEMINI_API_KEY=<gemini_api_key>
SUPABASE_PROJECT_URL=https://<supabase_project_url>
SUPABASE_SECRET_KEY=<supabase_secret_key>
```

The Postgres connection with ID `postgres_playroom_diet` is created via the env variable.

## Running locally

Using Astro CLI:

```sh
astro dev start
```

Access Airflow UI at `http://localhost:8080`

## Triggering the Dag

The backend triggers the Dag via REST API when a new scan is uploaded:

```
POST /api/v1/dags/process_scans/dagRuns
```

## Dynamic task mapping

With dynamic task mapping, you can write Dags that dynamically generate parallel tasks at runtime. This feature is used to parallelize all Gemini 3 interactions, so that the agents run in parallel with one task for each open scan that has been pulled from the database. Also, the final write of results to the database is parallelized this way.

However, to limit the parallelism, `max_active_tis_per_dag` has been configured for each of the tasks.

Since some tasks require to combine the result of various dynamically mapped task, e.g., `save_result` needs the combination of all agent outputs, the `zip` function is used to combine the individual outputs.
