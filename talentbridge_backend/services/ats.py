import requests
from datetime import datetime
from typing import List
from config import settings
from models import Job, JobSearchFilters, Application, ApplicationSummary, ApplicationCreate

AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}"
HEADERS = {
    "Authorization": f"Bearer {settings.AIRTABLE_API_KEY}",
    "Content-Type": "application/json",
}


def _airtable_list(table_name: str) -> list:
    url = f"{AIRTABLE_BASE_URL}/{table_name}"
    records = []
    offset = None

    while True:
        params = {}
        if offset:
            params["offset"] = offset
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break

    return records


def _airtable_create(table_name: str, fields: dict) -> dict:
    url = f"{AIRTABLE_BASE_URL}/{table_name}"
    payload = {"records": [{"fields": fields}]}
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["records"][0]


def search_jobs(filters: JobSearchFilters) -> List[Job]:
    raw_records = _airtable_list(settings.AIRTABLE_JOBS_TABLE)
    jobs: List[Job] = []

    for rec in raw_records:
        fields = rec.get("fields", {})
        status = fields.get("Status", "Open")
        if status != "Open":
            continue

        job = Job(
            job_id=fields.get("JobId", rec["id"]),
            title=fields.get("Title", ""),
            location=fields.get("Location"),
            role=fields.get("Role"),
            min_yoe=fields.get("MinYoE"),
            max_yoe=fields.get("MaxYoE"),
            skills=[s.strip() for s in (fields.get("Skills", "") or "").split(",") if s.strip()],
            salary_min=fields.get("SalaryMin"),
            salary_max=fields.get("SalaryMax"),
            status=status,
            description=fields.get("Description"),
        )

        # Simple filtering
        if filters.role and filters.role.lower() not in (job.role or "").lower():
            continue
        if filters.location and filters.location.lower() not in (job.location or "").lower():
            continue
        if filters.skills:
            lower_job_skills = {s.lower() for s in job.skills}
            if not any(skill.lower() in lower_job_skills for skill in filters.skills):
                continue
        if filters.min_yoe and job.max_yoe and job.max_yoe < filters.min_yoe:
            continue
        if filters.max_yoe and job.min_yoe and job.min_yoe > filters.max_yoe:
            continue

        jobs.append(job)

    return jobs


def get_job(job_id: str) -> Job | None:
    raw_records = _airtable_list(settings.AIRTABLE_JOBS_TABLE)
    for rec in raw_records:
        fields = rec.get("fields", {})
        if fields.get("JobId") == job_id or rec["id"] == job_id:
            return Job(
                job_id=fields.get("JobId", rec["id"]),
                title=fields.get("Title", ""),
                location=fields.get("Location"),
                role=fields.get("Role"),
                min_yoe=fields.get("MinYoE"),
                max_yoe=fields.get("MaxYoE"),
                skills=[s.strip() for s in (fields.get("Skills", "") or "").split(",") if s.strip()],
                salary_min=fields.get("SalaryMin"),
                salary_max=fields.get("SalaryMax"),
                status=fields.get("Status", "Open"),
                description=fields.get("Description"),
            )
    return None


def create_application(payload: ApplicationCreate, fit_score: float | None = None, ai_summary: str | None = None) -> Application:
    now = datetime.utcnow().isoformat()
    fields = {
        "AppId": "",  # we let Airtable assign, or set via formula
        "JobId": payload.job_id,
        "Name": payload.name,
        "Email": payload.email,
        "Phone": payload.phone,
        "ResumeUrl": payload.resume_url or "",
        "Status": "Applied",
        "FitScore": fit_score,
        "AISummary": ai_summary or "",
        "CreatedAt": now,
        "Events": "",
    }
    rec = _airtable_create(settings.AIRTABLE_APPS_TABLE, fields)
    f = rec["fields"]
    app_id = f.get("AppId", rec["id"])

    return Application(
        app_id=app_id,
        job_id=f.get("JobId", payload.job_id),
        name=f.get("Name", payload.name),
        email=f.get("Email", payload.email),
        phone=f.get("Phone", payload.phone),
        resume_url=f.get("ResumeUrl", payload.resume_url),
        status=f.get("Status", "Applied"),
        fit_score=f.get("FitScore"),
        ai_summary=f.get("AISummary"),
        created_at=datetime.fromisoformat(f.get("CreatedAt", now)),
        events=f.get("Events"),
    )


def get_applications_by_email(email: str) -> list[ApplicationSummary]:
    url = f"{AIRTABLE_BASE_URL}/{settings.AIRTABLE_APPS_TABLE}"
    # simple: list all then filter in python
    raw_records = _airtable_list(settings.AIRTABLE_APPS_TABLE)
    summaries: list[ApplicationSummary] = []

    for rec in raw_records:
        fields = rec.get("fields", {})
        if fields.get("Email", "").lower() != email.lower():
            continue

        app_id = fields.get("AppId", rec["id"])
        status = fields.get("Status", "Applied")
        fit = fields.get("FitScore")
        created_str = fields.get("CreatedAt")
        created = datetime.fromisoformat(created_str) if created_str else datetime.utcnow()

        # We don’t join with Jobs here to keep it simple
        job_title = fields.get("JobTitle")  # optional extra field in Airtable

        summaries.append(ApplicationSummary(
            app_id=app_id,
            job_title=job_title,
            status=status,
            fit_score=fit,
            created_at=created,
        ))

    return summaries
