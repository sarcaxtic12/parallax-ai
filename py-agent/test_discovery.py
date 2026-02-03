import sys
import os

# Add core to path
sys.path.append(os.path.join(os.getcwd(), 'core'))
sys.path.append(os.getcwd())

from core.discovery import generate_search_queries
from dotenv import load_dotenv

load_dotenv()

def test_queries():
    topic = "Is AI regulation necessary?"
    print(f"Testing Query Generation for topic: '{topic}'")
    
    # Ensure API Key is available
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not found in env.")
        # Fallback for manual testing if needed, but preferably read from .env
    
    queries = generate_search_queries(topic)
    print("\nGenerated Queries:")
    for q in queries:
        print(f"- {q}")

    if len(queries) >= 3:
        print("\nSUCCESS: Generated sufficient queries.")
    else:
        print("\nFAILURE: Did not generate enough queries.")

if __name__ == "__main__":
    test_queries()
