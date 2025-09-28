import json, os
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")

class JobMatcher:
    def __init__(self):
        try:
            with open('data/jobs_database.json', 'r') as f:
                self.jobs_data = json.load(f)
            print(f"✅ Loaded {len(self.jobs_data)} jobs")
        except Exception as e:
            print(f"❌ Error loading jobs: {e}")
            self.jobs_data = []
        
        texts = []
        for j in self.jobs_data:
            skills = ' '.join(j.get('required_skills', []) + j.get('preferred_skills', []))
            texts.append(f"{j['title']} {skills} {j.get('description','')}".lower())
        
        if texts:
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
            self.job_vectors = self.vectorizer.fit_transform(texts)
            self.model_ready = True
            print("✅ ML model ready")
        else:
            self.model_ready = False
            print("❌ No job data for ML model")

    def match_jobs(self, user_skills: List[str]) -> List[Dict]:
        # Fix: Check model_ready flag instead of job_vectors directly
        if not getattr(self, "model_ready", False) or not user_skills:
            return []
        
        vec = self.vectorizer.transform([' '.join(user_skills).lower()])
        sims = cosine_similarity(vec, self.job_vectors)[0]
        out = []
        
        for i, s in enumerate(sims):
            if s > 0.05:
                job = self.jobs_data[i]
                req = job.get('required_skills', [])
                user_lower = [x.lower() for x in user_skills]
                matching = [x for x in req if x.lower() in user_lower]
                out.append({
                    "job": job,
                    "match_score": round(s*100, 1),
                    "matching_skills": matching,
                    "total_required": len(req),
                    "explanation": f"You have {len(matching)}/{len(req)} required skills"
                })
        
        out.sort(key=lambda x: x['match_score'], reverse=True)
        return out[:10]
