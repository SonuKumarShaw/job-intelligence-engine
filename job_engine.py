import sqlite3
import hashlib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Job Intelligence Engine")
DB_NAME = "jobs.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_hash TEXT UNIQUE,
                title TEXT,
                company TEXT,
                skills TEXT,
                match_score REAL,
                url TEXT
            )
        """)

init_db()

class JobIn(BaseModel):
    title: str
    company: str
    description: str
    url: str

MY_SKILLS = {"python", "fastapi", "sql", "git", "linux", "automation", "api", "rest"}

def calculate_match(text: str) -> tuple[float, str]:
    words = set(text.lower().replace(",", " ").replace(".", " ").split())
    matched = MY_SKILLS.intersection(words)
    score = round((len(matched) / len(MY_SKILLS)) * 100, 1)
    return score, ", ".join(sorted(matched))

@app.post("/ingest-job")
def ingest_job(job: JobIn):
    job_hash = hashlib.md5(f"{job.company}-{job.title}-{job.url}".encode()).hexdigest()
    score, matched_skills = calculate_match(f"{job.title} {job.description}")

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO jobs (job_hash, title, company, skills, match_score, url) VALUES (?, ?, ?, ?, ?, ?)",
                (job_hash, job.title, job.company, matched_skills, score, job.url)
            )
        alert = "HIGH MATCH ALERT TRIGGERED!" if score >= 50 else "Saved to DB"
        return {"status": "inserted", "match_score": score, "matched_skills": matched_skills, "alert": alert}
    except sqlite3.IntegrityError:
        return {"status": "skipped", "reason": "Duplicate job listing"}

@app.get("/jobs")
def get_top_jobs(min_score: float = 0.0):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT title, company, skills, match_score, url FROM jobs WHERE match_score >= ? ORDER BY match_score DESC",
            (min_score,)
        ).fetchall()
    return {"count": len(rows), "jobs": [dict(r) for r in rows]}