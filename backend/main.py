import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from storage3.types import FileOptions
from supabase import create_client, Client
from postgrest.exceptions import APIError

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

# setup FastAPI app
app: FastAPI = FastAPI(title="Playroom Diet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Gemini Playroom Diet Backend"}


@app.get("/api/scan/{scan_id}")
def get_scan(scan_id: str):
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
async def create_scan(
    age: int = Form(...),
    file: UploadFile = File(...)
):
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
