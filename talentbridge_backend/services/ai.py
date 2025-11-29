from typing import Tuple
from config import settings
from models import Job, ApplicationCreate

# If you want real LLM, uncomment imports & add to requirements:
# import openai


def score_candidate(job: Job, app: ApplicationCreate) -> Tuple[float, str]:
    """
    Returns (fit_score, summary_text).
    For now: simple heuristic stub.
    """

    # Very naive scoring for demo:
    score = 60.0

    if job.role and job.role.lower() in app.resume_url.lower():
        score += 10

    if job.location and job.location.lower() in app.resume_url.lower():
        score += 5

    summary = (
        f"Candidate {app.name} applied for {job.title}. "
        f"Email: {app.email}, Phone: {app.phone}. "
        "Preliminary heuristic fit score computed."
    )

    # Real LLM:
    # if settings.OPENAI_API_KEY:
    #     openai.api_key = settings.OPENAI_API_KEY
    #     prompt = f"""
    #     Job: {job.title}
    #     Description: {job.description}
    #     Candidate: {app.name}
    #     Resume URL: {app.resume_url}
    #
    #     Analyze how well this candidate fits this job on a 0-100 scale.
    #     Return JSON with keys: fit_score, summary.
    #     """
    #     resp = openai.ChatCompletion.create(
    #         model="gpt-4o-mini",
    #         messages=[{"role": "user", "content": prompt}],
    #     )
    #     # Parse resp into score, summary (omitted here for brevity).

    return score, summary


def query_to_filters(query: str) -> dict:
    """
    Stub: convert natural language query to filter dict.
    You can later do this with LLM; for now, return very loose filters.
    """
    # Very naive: if user types "intern", treat role = "intern".
    filters: dict = {}
    ql = query.lower()
    if "intern" in ql:
        filters["role"] = "intern"
    if "remote" in ql:
        filters["location"] = "remote"
    return filters
