from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv, find_dotenv
from services.job_matcher import JobMatcher
from services.interview_coach import InterviewCoach
import warnings
warnings.filterwarnings("ignore")

load_dotenv(find_dotenv())
app = FastAPI(title="Career Optimization Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_matcher = JobMatcher()
interview_coach = InterviewCoach()

class UserSkills(BaseModel):
    skills: List[str]
    experience_level: Optional[str] = "Mid"
    location: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None

class InterviewRequest(BaseModel):
    job_title: str
    company: Optional[str] = None

class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str

@app.get("/")
async def root():
    return {"message": "Career Optimization Engine API", "status": "running"}

@app.get("/api/locations")
async def get_locations():
    try:
        locations = job_matcher.get_unique_locations()
        return {"success": True, "locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match-jobs")
async def match_jobs(request: UserSkills):
    try:
        filtered_jobs = job_matcher.filter_jobs(
            location=request.location,
            min_salary=request.min_salary,
            max_salary=request.max_salary
        )

        matches = job_matcher.match_jobs(request.skills, filtered_jobs)
        return {
            "success": True,
            "user_skills": request.skills,
            "total_matches": len(matches),
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/generate-questions")
async def generate_questions(request: InterviewRequest):
    try:
        session = interview_coach.generate_questions(request.job_title, request.company)
        return {"success": True, "session": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/analyze-answer")
async def analyze_answer(request: AnswerRequest):
    try:
        feedback = interview_coach.analyze_answer(request.session_id, request.question_id, request.answer)
        if "error" in feedback:
            raise HTTPException(status_code=404, detail=feedback["error"])
        return {"success": True, "feedback": feedback}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Career Optimization Engine Starting...")
    print("📍 http://localhost:8000")
    print("📖 http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
