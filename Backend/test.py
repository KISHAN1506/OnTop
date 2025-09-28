# debug_env.py
import os
from dotenv import load_dotenv, find_dotenv

print("Current directory:", os.getcwd())
print("Looking for .env file...")

# Try to find .env
env_file = find_dotenv()
print(f"Found .env at: {env_file}")

# Load it
load_dotenv(find_dotenv())

# Check if loaded
key = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY loaded: {'YES' if key else 'NO'}")
if key:
    print(f"Key starts with: {key[:10]}...")
else:
    print("Key is None or empty")
