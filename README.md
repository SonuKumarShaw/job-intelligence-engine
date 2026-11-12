# Autonomous Job & Internship Intelligence Engine

A Python backend service built with **FastAPI** and **SQLite** that ingests job listings, prevents duplicates using MD5 hashing, scores skill alignment, and serves ranked opportunities via REST API endpoints.

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Database:** SQLite3

## How to Run Locally
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   Start the server:

Bash
python -m uvicorn job_engine:app --reload
Open interactive Swagger docs at http://127.0.0.1:8000/docs
