import google.generativeai as genai
import json, os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from typing import Dict
import warnings
warnings.filterwarnings("ignore")

# Load API key from .env
load_dotenv(find_dotenv())
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class InterviewCoach:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.sessions: Dict[str, Dict] = {}

    def generate_questions(self, job_title: str, company: str = None) -> Dict:
        try:
            company_text = f" at {company}" if company else ""
            prompt = f"""
            Generate 5 interview questions for {job_title}{company_text}.
            Include: 2 behavioral, 2 technical, 1 general.
            Return JSON:
            {{
              "questions":[
                {{"id":1,"question":"Tell me about yourself","type":"general"}}
              ]
            }}
            """
            txt = self.model.generate_content(prompt).text.strip()

            # Remove ```json fences if AI wraps the output
            if txt.startswith("```json"):
                txt = txt[7:-3].strip()
            elif txt.startswith("```"):
                txt = txt[3:-3].strip()

            data = json.loads(txt)

            sid = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            sess = {
                "session_id": sid,
                "job_title": job_title,
                "company": company,
                "questions": data.get("questions", []),
                "answers": {}
            }
            self.sessions[sid] = sess

            # 🖥️ Pretty print for terminal
            print(f"\n🎯 Interview Questions for {job_title}")
            if company:
                print(f"📍 Company: {company}")
            print("=" * 50)

            for i, q in enumerate(sess["questions"], 1):
                print(f"\n{i}. [{q['type'].upper()}] {q['question']}")

            return sess
        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            # Fallback if JSON parsing fails
            sid = f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            fb = {
                "session_id": sid,
                "job_title": job_title,
                "questions": [
                    {"id": 1, "question": "Tell me about yourself", "type": "general"},
                    {"id": 2, "question": "Why do you want this job?", "type": "behavioral"}
                ],
                "answers": {}
            }
            self.sessions[sid] = fb
            return fb

    def analyze_answer(self, session_id: str, question_id: int, answer: str) -> Dict:
        s = self.sessions.get(session_id)
        if not s:
            return {"error": "Session not found"}

        q = next((x for x in s["questions"] if x["id"] == question_id), None)
        if not q:
            return {"error": "Question not found"}

        try:
            prompt = f"""
            Analyze this interview answer and return JSON:
            Question: {q['question']}
            Answer: {answer}
            JSON: {{
              "score": 7,
              "strengths": ["..."],
              "improvements": ["..."],
              "feedback": "..."
            }}
            Score 1-10.
            """
            txt = self.model.generate_content(prompt).text.strip()

            # Handle JSON inside fences
            if txt.startswith("```json"):
                txt = txt[7:-3].strip()
            elif txt.startswith("```"):
                txt = txt[3:-3].strip()

            fb = json.loads(txt)

            s["answers"][question_id] = {
                "answer": answer,
                "feedback": fb,
                "timestamp": datetime.now().isoformat()
            }

            # 🖥️ Pretty print
            print(f"\n📊 Your Score: {fb['score']}/10")
            print("\n✅ Strengths:")
            for strength in fb.get('strengths', []):
                print(f"  • {strength}")

            print("\n🔧 Areas to Improve:")
            for improvement in fb.get('improvements', []):
                print(f"  • {improvement}")

            print(f"\n💡 Overall Feedback:\n{fb.get('feedback', 'Good effort!')}")

            return fb
        except Exception as e:
            print(f"❌ Error analyzing answer: {e}")
            # Fallback analysis
            fb = {
                "score": 6,
                "strengths": ["Clear communication"],
                "improvements": ["Add concrete examples"],
                "feedback": "Good answer, add more specifics"
            }
            s["answers"][question_id] = {
                "answer": answer,
                "feedback": fb,
                "timestamp": datetime.now().isoformat()
            }
            return fb
