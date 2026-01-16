import os
import uuid
from datetime import datetime, date
from time import time

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from storage3.types import FileOptions
from supabase import create_client, Client

from airflow import AirflowClient

load_dotenv()

# setup Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

# setup Airflow client
AIRFLOW_HOST = os.getenv("AIRFLOW_HOST", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")
AIRFLOW_STATIC_TOKEN = os.getenv("AIRFLOW_STATIC_TOKEN") or None

airflow_client: AirflowClient = AirflowClient(
    AIRFLOW_HOST,
    AIRFLOW_USERNAME,
    AIRFLOW_PASSWORD,
    AIRFLOW_STATIC_TOKEN
)

# rate limiting config
DAILY_SCAN_LIMIT = int(os.getenv("DAILY_SCAN_LIMIT", "20"))
GET_RATE_LIMIT = os.getenv("GET_RATE_LIMIT", "30/minute")
POST_RATE_LIMIT = os.getenv("POST_RATE_LIMIT", "5/minute")

limiter = Limiter(key_func=get_remote_address)

# cache for daily scan count (5 second TTL)
_scan_count_cache: dict = {"count": 0, "timestamp": 0}
CACHE_TTL_SECONDS = 5

# setup FastAPI app
app: FastAPI = FastAPI(title="Playroom Diet API")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_today_scan_count(bypass_cache: bool = False) -> int:
    now = time()
    if not bypass_cache and now - _scan_count_cache["timestamp"] < CACHE_TTL_SECONDS:
        return _scan_count_cache["count"]

    today_start = date.today().isoformat()
    result = supabase.table("scans").select("id", count="exact").gte("created_at", today_start).execute()
    count = result.count or 0

    _scan_count_cache["count"] = count
    _scan_count_cache["timestamp"] = now
    return count


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Gemini Playroom Diet Backend"}


@app.get("/api/limits")
@limiter.limit(GET_RATE_LIMIT)
def get_limits(request: Request):
    current_count = get_today_scan_count()
    return {
        "daily_scan_limit": DAILY_SCAN_LIMIT,
        "scans_today": current_count,
        "scans_remaining": max(0, DAILY_SCAN_LIMIT - current_count)
    }


@app.get("/api/scan/{scan_id}")
@limiter.limit(GET_RATE_LIMIT)
def get_scan(request: Request, scan_id: str):
    try:
        result = supabase.table("scans").select("*").eq("id", scan_id).execute()
    except APIError:
        raise HTTPException(status_code=404, detail="Scan not found")

    if not result.data:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan = result.data[0]

    return {
        "scan_id": scan_id,
        "status": scan["status"],
        "result": scan.get("results_json") if scan["status"] == "done" else None
    }


@app.post("/api/scan")
@limiter.limit(POST_RATE_LIMIT)
async def create_scan(
    request: Request,
    age: int = Form(...),
    file: UploadFile = File(...)
):
    # check daily limit (bypass cache for accurate count)
    current_count = get_today_scan_count(bypass_cache=True)
    if current_count >= DAILY_SCAN_LIMIT:
        raise HTTPException(status_code=429, detail="Daily scan limit reached")

    try:
        # upload file
        file_content = await file.read()
        file_ext = file.filename.split(".")[-1]

        scan_id = str(uuid.uuid4())
        file_path = f"scans/{scan_id}.{file_ext}"

        mime_type = file.content_type or "image/jpeg"
        file_options: FileOptions = {"content-type": mime_type}
        supabase.storage.from_("playroom-images").upload(
            path=file_path,
            file=file_content,
            file_options=file_options
        )

        # insert scan row
        data = {
            "id": scan_id,
            "child_age": age,
            "image_path": file_path,
            "status": "processing",
            "created_at": datetime.now().isoformat()
        }
        supabase.table("scans").insert(data).execute()

        # trigger Airflow Dag
        dag_run_id = airflow_client.trigger_dag("process_scans")

        return {"scan_id": scan_id, "dag_run_id": dag_run_id}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
