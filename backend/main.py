import hashlib
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
from supabase import create_client, Client

from airflow import AirflowClient

load_dotenv()

supabase: Client | None = None
airflow_client: AirflowClient | None = None

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SECRET_KEY", "")
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY")
        supabase = create_client(url, key)
    return supabase

def get_airflow() -> AirflowClient:
    global airflow_client
    if airflow_client is None:
        host = os.getenv("AIRFLOW_HOST", "http://localhost:8080")
        username = os.getenv("AIRFLOW_USERNAME", "airflow")
        password = os.getenv("AIRFLOW_PASSWORD", "airflow")
        token = os.getenv("AIRFLOW_STATIC_TOKEN") or None
        airflow_client = AirflowClient(host, username, password, token)
    return airflow_client

DAILY_SCAN_LIMIT = int(os.getenv("DAILY_SCAN_LIMIT", "20"))
GET_RATE_LIMIT = os.getenv("GET_RATE_LIMIT", "30/minute")
POST_RATE_LIMIT = os.getenv("POST_RATE_LIMIT", "5/minute")
limiter = Limiter(key_func=get_remote_address)

_scan_count_cache = {"count": 0, "timestamp": 0}
CACHE_TTL_SECONDS = 5

app = FastAPI(title="Playroom Diet API")
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
    result = get_supabase().table("scans").select("id", count="exact").gte("created_at", today_start).execute()
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
        result = get_supabase().table("scans").select("*").eq("id", scan_id).execute()
    except APIError:
        raise HTTPException(status_code=404, detail="Scan not found")

    if not result.data:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan = result.data[0]
    image_url = get_supabase().storage.from_("playroom-images").get_public_url(scan["image_path"]) if scan.get("image_path") else None

    return {
        "scan_id": scan_id,
        "status": scan["status"],
        "image_url": image_url,
        "result": scan.get("results_json") if scan["status"] == "done" else None
    }


@app.post("/api/scan")
@limiter.limit(POST_RATE_LIMIT)
async def create_scan(
    request: Request,
    age: int = Form(...),
    file: UploadFile = File(...)
):
    try:
        file_content = await file.read()
        image_hash = hashlib.sha256(file_content).hexdigest()

        existing = get_supabase().table("scans").select("id, status").eq("image_hash", image_hash).execute()
        if existing.data:
            existing_scan = existing.data[0]
            return {"scan_id": existing_scan["id"], "cached": True, "status": existing_scan["status"]}

        current_count = get_today_scan_count(bypass_cache=True)
        if current_count >= DAILY_SCAN_LIMIT:
            raise HTTPException(status_code=429, detail="Daily scan limit reached")

        scan_id = str(uuid.uuid4())
        file_ext = file.filename.split(".")[-1]
        file_path = f"scans/{scan_id}.{file_ext}"

        get_supabase().storage.from_("playroom-images").upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type or "image/jpeg"}
        )

        get_supabase().table("scans").insert({
            "id": scan_id,
            "child_age": age,
            "image_path": file_path,
            "image_hash": image_hash,
            "status": "processing",
            "created_at": datetime.now().isoformat()
        }).execute()

        dag_run_id = get_airflow().trigger_dag("process_scans")
        return {"scan_id": scan_id, "dag_run_id": dag_run_id, "cached": False}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
