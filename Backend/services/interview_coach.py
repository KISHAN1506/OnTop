import google.generativeai as genai
import json, os, re, warnings
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from typing import Dict

warnings.filterwarnings("ignore")

# Load API key from .env and configure the library at the module level
load_dotenv(find_dotenv())
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    print("🔑 API Key loaded and configured successfully.")
else:
    print("❌ No API key found in environment. The application will use fallback responses.")


class InterviewCoach:
    def __init__(self):
        if api_key:
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            self.sessions: Dict[str, Dict] = {}
            print("✅ Interview Coach initialized with a working API key.")
        else:
            self.model = None
            self.sessions: Dict[str, Dict] = {}
            print("❌ Interview Coach initialized WITHOUT an API key. Using fallbacks.")

    def _clean_json(self, text: str) -> str:
        """Remove markdown fences and extract JSON only."""
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r"```(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def generate_questions(self, job_title: str, company: str = None) -> Dict:
        if not self.model:
            return self._get_fallback_questions(job_title, company)

        try:
            company_text = f" at {company}" if company else ""
            prompt = f"""
            Generate exactly 5 interview questions for a {job_title} position{company_text}.
            Include: 2 behavioral, 2 technical, and 1 general question.
            Return ONLY a JSON object in this exact format:
            {{
              "questions": [
                {{"id": 1, "question": "...", "type": "general"}},
                {{"id": 2, "question": "...", "type": "behavioral"}},
                {{"id": 3, "question": "...", "type": "technical"}},
                {{"id": 4, "question": "...", "type": "behavioral"}},
                {{"id": 5, "question": "...", "type": "technical"}}
              ]
            }}
            """

            response = self.model.generate_content(prompt)
            txt = self._clean_json(response.text)

            data = json.loads(txt)
            questions = data.get("questions", [])

            if len(questions) != 5:
                raise ValueError(f"Expected 5 questions, but Gemini returned {len(questions)}")

            sid = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            sess = {
                "session_id": sid,
                "job_title": job_title,
                "company": company,
                "questions": questions,
                "answers": {},
            }
            self.sessions[sid] = sess
            return sess

        except Exception as e:
            print(f"❌ Error generating questions from API: {e}. Using fallback.")
            return self._get_fallback_questions(job_title, company)

    def _get_fallback_questions(self, job_title: str, company: str = None):
        print("⚠️ Using fallback questions.")
        sid = f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fallback_questions = [
            {"id": 1, "question": "Tell me about yourself and your background.", "type": "general"},
            {"id": 2, "question": "Describe a challenging project you worked on and how you overcame obstacles.", "type": "behavioral"},
            {"id": 3, "question": f"What technical skills are most important for a {job_title} role?", "type": "technical"},
            {"id": 4, "question": "How do you handle working under pressure and tight deadlines?", "type": "behavioral"},
            {"id": 5, "question": f"What tools and technologies do you use in your {job_title} work?", "type": "technical"},
        ]

        fb_session = {
            "session_id": sid,
            "job_title": job_title,
            "company": company,
            "questions": fallback_questions,
            "answers": {},
        }
        self.sessions[sid] = fb_session
        return fb_session

    # You can copy your working analyze_answer() from before here
    def analyze_answer(self, session_id: str, question_id: int, answer: str) -> Dict:
        # Placeholder
        return {"note": "Use your earlier analyze_answer implementation here"}