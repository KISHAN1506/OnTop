from services.job_matcher import JobMatcher
from services.interview_coach import InterviewCoach
import warnings
warnings.filterwarnings("ignore")

def demo_job_matching():
    print("🔍 JOB MATCHING DEMO")
    print("=" * 30)
    matcher = JobMatcher()
    skills = ["Python", "Machine Learning", "SQL"]
    matches = matcher.match_jobs(skills)
    
    print(f"Your skills: {', '.join(skills)}")
    print(f"Found {len(matches)} matching jobs:\n")
    
    for i, match in enumerate(matches[:3], 1):  # Show top 3 only
        job = match['job']
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Match: {match['match_score']}% | Salary: ${job['salary_min']:,}-${job['salary_max']:,}")
        print(f"   Location: {job['location']}")
        print(f"   You have: {', '.join(match['matching_skills'])}")
        print()

def demo_interview_coach():
    print("🎤 INTERVIEW COACHING DEMO")
    print("=" * 35)
    coach = InterviewCoach()
    session = coach.generate_questions("Data Scientist", "Google")
    
    print(f"\n🗣️  Sample Answer Analysis:")
    print("-" * 30)
    sample_answer = "I'm passionate about data science because I love solving complex problems with data and creating insights that drive business decisions."
    feedback = coach.analyze_answer(session['session_id'], 1, sample_answer)

if __name__ == "__main__":
    demo_job_matching()
    print("\n" + "="*50 + "\n")
    demo_interview_coach()
