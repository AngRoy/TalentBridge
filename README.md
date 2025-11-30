# TalentBridge · AI-assisted Recruitment Concierge

> **Category:** Zoho SalesIQ – Website Bot  
> **Built for:** Cliqtrix (Zoho’s annual app-building contest)  
> **Stack:** Zoho SalesIQ Zobot (Codeless + Plugs) · FastAPI · Python · ATS backend (e.g. Airtable) · OTP + AI scoring

TalentBridge turns a static “Careers” page into an **interactive recruitment concierge**.  
It combines Zoho SalesIQ’s **Zobot** and **Plugs** with a custom FastAPI backend and a lightweight ATS to:

- guide candidates to the right roles,  
- verify and submit applications,  
- generate AI-powered fit scores & summaries, and  
- let candidates **track their status** directly inside the chat widget.

The entire system is hackathon-friendly: clean architecture, clear boundaries, and easy to demo end-to-end.

---

## Table of Contents

- [Problem & Vision](#problem--vision)
- [Key Features](#key-features)
- [High-Level Architecture](#high-level-architecture)
- [Repository Layout](#repository-layout)
- [Getting Started](#getting-started)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Backend Setup (FastAPI)](#2-backend-setup-fastapi)
  - [3. ATS Setup (example: Airtable)](#3-ats-setup-example-airtable)
  - [4. Zoho SalesIQ · Zobot & Plugs](#4-zoho-salesiq--zobot--plugs)
  - [5. Landing Page](#5-landing-page)
- [Usage & Demo Flows](#usage--demo-flows)
  - [Candidate Journey](#candidate-journey)
  - [Recruiter / HR View](#recruiter--hr-view)
- [Implementation Details](#implementation-details)
  - [SalesIQ Plugs](#salesiq-plugs)
  - [Backend Services](#backend-services)
- [Extending TalentBridge](#extending-talentbridge)
- [Roadmap](#roadmap)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Problem & Vision

Traditional careers pages are:

- static,
- form-heavy, and
- disconnected from real ATS workflows.

Candidates don’t know which role fits them, and recruiters drown in unprioritised resumes.

**TalentBridge** reimagines this as a **conversational recruitment concierge**:

- Candidates chat with a bot on the website (via **Zoho SalesIQ Zobot**),
- the bot uses **Plugs** to call out to a custom backend, and
- the backend talks to an ATS and an AI model to pre-screen and score each candidate.

Zoho’s official docs describe **Plugs** as the way to perform custom actions and third-party integrations from a codeless bot, such as OTP checks or external APIs. :contentReference[oaicite:0]{index=0}  
TalentBridge leans hard into that model and builds a full HR mini-stack on top of it.

---

## Key Features

### For Candidates

- **Conversational job discovery**  
  Bot asks for role, skills, experience, and location, then calls a `FindJobs` plug which queries the ATS and returns curated openings.

- **Guided application flow with OTP verification**  
  Candidate confirms a job, shares contact details + resume URL, and passes an OTP check before the application is created – implemented using `SendOtp` and `VerifyOtp` Plugs.

- **Application tracking inside chat**  
  “My applications” lets candidates see previously submitted applications (status, basic details) via a `GetApplications` plug mapped to an ATS query.

### For Recruiters / HR

- **AI-generated fit scores & summaries**  
  When an application is created, the backend computes a **fit score** and a short recruiter-friendly summary using an AI scoring service (pluggable LLM). :contentReference[oaicite:1]{index=1}  

- **ATS-agnostic integration layer**  
  `ats.py` isolates all ATS operations (currently Airtable example). Swapping to a different ATS (Notion, real HR tool) only touches this layer.

- **Bot built with Codeless + Plugs**  
  Judges can see strong usage of Zoho’s ecosystem:
  - Codeless Zobot for conversation design,
  - **Plugs** for OTP, AI, ATS integration, as recommended in the SalesIQ docs. :contentReference[oaicite:2]{index=2}  

### Engineering Highlights

- Modern **FastAPI** backend for high-performance APIs and clean type-hints. :contentReference[oaicite:3]{index=3}  
- Clear service boundaries: `ats.py`, `otp.py`, `ai.py`.  
- Hackathon-friendly deployment (Render / Railway / etc.).  
- Static landing page (`index.html`) designed to look like a polished product site and wired to open the SalesIQ widget.

---

## High-Level Architecture

**Flow:**

1. Visitor lands on `index.html` → **Zoho SalesIQ widget** loads.
2. Visitor clicks the widget → **Zobot (codeless)** greets them and offers:
   - Find a job
   - Apply with Job ID
   - My applications
   - Ask the recruiter
3. At key steps, Zobot triggers **Plugs**:
   - `FindJobsPlug` → POST `/jobs/search` on backend.
   - `CreateApplicationPlug` → POST `/applications`.
   - `GetApplicationsPlug` → GET `/applications/by-email`.
   - `SendOtpPlug` / `VerifyOtpPlug` → POST `/otp/send`, `/otp/verify`.
4. **FastAPI backend**:
   - validates inputs,
   - talks to **ATS** through `ats.py`, and
   - calls `ai.score_candidate` to generate fit scores & summaries.
5. ATS stores all job postings and application data; Zobot reads back status via plugs.

This mirrors how Zoho’s sample plugs integrate with external systems (CRM, e-commerce, OpenAI integrations, etc.), but adapted to recruitment. :contentReference[oaicite:4]{index=4}  

---

## Repository Layout

```text
TALENTBRIDGE/
├── SalesIQ_Script/           # Deluge / SalesIQ Script for all Plugs
│   ├── CreateApplicationPlug/
│   ├── FindJobsPlug/
│   ├── GetApplicationsPlug/
│   ├── SendOtpPlug/
│   └── VerifyOtpPlug/
│
├── talentbridge_backend/     # FastAPI backend (Python)
│   ├── services/
│   │   ├── ai.py             # AI scoring & NL → filter helpers
│   │   ├── ats.py            # ATS integration (e.g. Airtable)
│   │   └── otp.py            # In-memory OTP generation & verification
│   ├── __init__.py
│   ├── config.py             # Pydantic Settings / env variables
│   ├── main.py               # FastAPI app & routes
│   └── models.py             # Pydantic models shared across endpoints
│
├── index.html                # Landing page + Zoho SalesIQ widget embed
├── requirements.txt          # Python dependencies (FastAPI, requests, etc.)
├── .env.example              # Sample env file (recommended to create)
├── LICENSE
└── README.md                 # You are here 🚀
