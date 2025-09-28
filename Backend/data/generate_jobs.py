import google.generativeai as genai
import json, os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load API key from .env
load_dotenv(find_dotenv())
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_job_dataset():
    # Use latest available model
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = """
    Generate exactly 30 realistic tech job postings as a JSON array.
    
    For each job, use this exact structure:
    {
        "id": 1,
        "title": "Frontend Developer",
        "company": "TechCorp Inc", 
        "location": "San Francisco, CA",
        "remote_option": true,
        "salary_min": 90000,
        "salary_max": 120000,
        "required_skills": ["React", "JavaScript", "CSS", "HTML"],
        "preferred_skills": ["TypeScript", "Node.js"],
        "experience_level": "Mid",
        "company_size": "50-200",
        "description": "Build responsive web applications using React"
    }

    Include variety:
    - Job titles: Frontend Developer, Backend Developer, Full Stack Developer, Data Scientist, DevOps Engineer
    - Locations: San Francisco CA, New York NY, Austin TX, Seattle WA, Remote
    - Realistic 2024 salaries
    - Different experience levels: Entry, Mid, Senior

    Return ONLY valid JSON array, no other text.
    """

    try:
        print("Generating jobs with AI...")
        resp = model.generate_content(prompt)
        text = resp.text.strip()

        # Clean markdown fences if present
        text = text.replace("```json", "").replace("```", "").strip()

        # Parse JSON
        jobs = json.loads(text)

        # Save to file
        os.makedirs("data", exist_ok=True)
        with open("data/jobs_database.json", "w") as f:
            json.dump(jobs, f, indent=2)

        print(f"✅ Generated {len(jobs)} jobs successfully!")
        return jobs

    except Exception as e:
        print(f"❌ Error: {e}")
        fallback = [{
            "id": 1,
            "title": "Frontend Developer",
            "company": "TechStart Inc",
            "location": "San Francisco, CA",
            "remote_option": True,
            "salary_min": 90000,
            "salary_max": 120000,
            "required_skills": ["React", "JavaScript", "CSS"],
            "preferred_skills": ["TypeScript"],
            "experience_level": "Mid",
            "company_size": "50-200",
            "description": "Build modern web applications"
        }]

        with open("data/jobs_database.json", "w") as f:
            json.dump(fallback, f, indent=2)

        print("✅ Created fallback job data")
        return fallback

if __name__ == "__main__":
    generate_job_dataset()
