import uuid
from fastapi import APIRouter, HTTPException
from fastapi.background import BackgroundTasks
from app.services.bulk_service import bulk_service
from app.config import settings

router = APIRouter(prefix="/bulk", tags=["bulk"])

# In-memory storage for jobs
jobs = {}


def run_bulk_enrichment(job_id: str):
    """Background task to run bulk enrichment"""
    try:
        jobs[job_id]["status"] = "processing"
        data = bulk_service.enrich_excel(return_json=True)
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["data"] = data
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@router.post("/enrich")
def enrich_excel(background_tasks: BackgroundTasks):
    """Start bulk enrichment in background"""
    if not settings.LUSHA_API_KEY:
        raise HTTPException(status_code=500, detail="LUSHA_API_KEY not configured")

    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "started",
        "data": None,
        "error": None
    }

    background_tasks.add_task(run_bulk_enrichment, job_id)

    return {"job_id": job_id, "status": "started"}


@router.get("/enrich/{job_id}")
def get_enrichment_status(job_id: str):
    """Get enrichment job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    response = {"status": job["status"]}

    if job["status"] == "completed":
        response["data"] = job["data"]
    elif job["status"] == "failed":
        response["error"] = job.get("error")

    return response
