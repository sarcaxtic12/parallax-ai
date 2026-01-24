import requests
import os
from typing import List, Dict, Any

GO_SCRAPER_HOST = os.getenv("GO_SCRAPER_HOST", "localhost")
GO_SCRAPER_PORT = os.getenv("GO_SCRAPER_PORT", "8080")
GO_SCRAPER_URL = os.getenv("GO_SCRAPER_URL", f"http://{GO_SCRAPER_HOST}:{GO_SCRAPER_PORT}/scrape")

def fetch_articles(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches article content from the Go scraping service.
    Retries up to 3 times to handle "Cold Start" on Render Free Tier.
    """
    max_retries = 3
    import time
    
    for attempt in range(max_retries):
        try:
             print(f"DEBUG: Calling Scraper (Attempt {attempt+1}/{max_retries})...")
             response = requests.post(
                 GO_SCRAPER_URL, 
                 json={"urls": urls}, 
                 timeout=60
             )
             response.raise_for_status()
             
             data = response.json()
             if not data:
                 print(f"DEBUG: Scraper returned empty list on attempt {attempt+1}")
                 if attempt < max_retries - 1:
                     time.sleep(2)
                     continue
                     
             return data

        except Exception as e:
             print(f"DEBUG: Scraper Error (Attempt {attempt+1}): {e}")
             if attempt < max_retries - 1:
                 time.sleep(2)
             else:
                 print("DEBUG: Scraper failed after max retries.")
                 return []
    return []
