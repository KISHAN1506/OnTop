import json
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
            texts.append(f"{j.get('title','')} {skills} {j.get('description','')}".lower())
        
        if texts:
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
            self.job_vectors = self.vectorizer.fit_transform(texts)
            print("✅ ML model ready")
        else:
            self.vectorizer = None
            self.job_vectors = None
            print("❌ No job data for ML model")

    def get_unique_locations(self):
        locations = set()
        for job in self.jobs_data:
            location = job.get('location', '')
            if location:
                locations.add(location)
        return sorted(list(locations))

    def filter_jobs(self, location=None, min_salary=None, max_salary=None):
        filtered = self.jobs_data
        
        if location:
            filtered = [job for job in filtered if job.get('location') == location]

        if min_salary is not None:
            filtered = [job for job in filtered if job.get('salary_min', 0) >= min_salary]

        if max_salary is not None:
            filtered = [job for job in filtered if job.get('salary_max', 0) <= max_salary]

        return filtered

    def match_jobs(self, user_skills: List[str], jobs: List[Dict] = None) -> List[Dict]:
        if not user_skills:
            return []

        if jobs is None:
            jobs = self.jobs_data
        
        texts = []
        for j in jobs:
            skills = ' '.join(j.get('required_skills', []) + j.get('preferred_skills', []))
            texts.append(f"{j.get('title','')} {skills} {j.get('description','')}".lower())

        if not texts or not self.vectorizer:
            return []

        vec = self.vectorizer.transform([' '.join(user_skills).lower()])
        job_vectors = self.vectorizer.transform(texts)
        sims = cosine_similarity(vec, job_vectors)[0]

        out = []
        user_lower = [x.lower() for x in user_skills]
        for i, s in enumerate(sims):
            if s > 0.05:
                job = jobs[i]
                req = job.get('required_skills', [])
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