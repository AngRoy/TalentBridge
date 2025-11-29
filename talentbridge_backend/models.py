from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Job(BaseModel):
    job_id: str
    title: str
    location: Optional[str] = None
    role: Optional[str] = None
    min_yoe: Optional[int] = None
    max_yoe: Optional[int] = None
    skills: List[str] = []
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None


class JobSearchFilters(BaseModel):
    role: Optional[str] = None
    skills: List[str] = []
    min_yoe: Optional[int] = None
    max_yoe: Optional[int] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None


class ApplicationCreate(BaseModel):
    job_id: str
    name: str
    email: EmailStr
    phone: str
    resume_url: Optional[str] = None


class Application(BaseModel):
    app_id: str
    job_id: str
    name: str
    email: EmailStr
    phone: str
    resume_url: Optional[str] = None
    status: str
    fit_score: Optional[float] = None
    ai_summary: Optional[str] = None
    created_at: datetime
    events: Optional[str] = None  # JSON string or text


class ApplicationSummary(BaseModel):
    app_id: str
    job_title: Optional[str] = None
    status: str
    fit_score: Optional[float] = None
    created_at: datetime


class OTPRequest(BaseModel):
    phone: str
    channel: str = "sms"  # or "email"


class OTPVerify(BaseModel):
    phone: str
    otp: str


class QueryToFilter(BaseModel):
    query: str


class QueryToFilterResult(BaseModel):
    filters: JobSearchFilters