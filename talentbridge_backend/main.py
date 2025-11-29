from fastapi import FastAPI, HTTPException
from typing import List

from config import settings
from models import (
    Job, JobSearchFilters,
    ApplicationCreate, Application, ApplicationSummary,
    OTPRequest, OTPVerify,
    QueryToFilter, QueryToFilterResult,
)
from services import ats, otp, ai

app = FastAPI(title="TalentBridge Backend")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs/search", response_model=List[Job])
def search_jobs(filters: JobSearchFilters):
    return ats.search_jobs(filters)


@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: str):
    job = ats.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/applications", response_model=Application)
def create_application(app_payload: ApplicationCreate):
    job = ats.get_job(app_payload.job_id)
    if not job:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    fit_score, summary = ai.score_candidate(job, app_payload)
    application = ats.create_application(app_payload, fit_score=fit_score, ai_summary=summary)
    return application


@app.get("/applications/by-email", response_model=List[ApplicationSummary])
def list_applications(email: str):
    return ats.get_applications_by_email(email)


@app.post("/otp/send")
def send_otp(req: OTPRequest):
    # For now we just generate & log OTP
    otp_code = otp.generate_and_store_otp(req.phone)
    # In real system, send via SMS/email provider here.
    return {"success": True}


@app.post("/otp/verify")
def verify_otp(req: OTPVerify):
    ok = otp.verify_otp(req.phone, req.otp)
    return {"verified": ok}


@app.post("/ai/query-to-filter", response_model=QueryToFilterResult)
def query_to_filter(payload: QueryToFilter):
    filter_dict = ai.query_to_filters(payload.query)
    filters = JobSearchFilters(**filter_dict)
    return QueryToFilterResult(filters=filters)