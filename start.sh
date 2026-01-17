#!/bin/bash

cleanup() {
    echo "Shutting down..."
    kill $(jobs -p) 2>/dev/null

    echo "Stopping Airflow..."
    (cd airflow && astro dev kill)
    exit
}

trap cleanup SIGINT

# Airflow
echo "--- Starting Airflow ---"
(cd airflow && astro dev kill && astro dev start)

# Frontend
echo "--- Starting Frontend ---"
(cd frontend && npm run dev -- --host) &

# Backend
echo "--- Starting Backend ---"
(cd backend && uv run python -m uvicorn main:app --reload --host 0.0.0.0) &

# Wait
wait
