import requests
import os
from typing import List, Dict, Any

GO_SCRAPER_HOST = os.getenv("GO_SCRAPER_HOST", "localhost")
GO_SCRAPER_PORT = os.getenv("GO_SCRAPER_PORT", "8080")
GO_SCRAPER_URL = os.getenv("GO_SCRAPER_URL", f"http://{GO_SCRAPER_HOST}:{GO_SCRAPER_PORT}/scrape")

def fetch_articles(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches article content from the Go scraping service.
    
    Args:
        urls: List of URLs to scrape.
        
    Returns:
        List of dictionaries containing scraped article data.
        Returns an empty list if the request fails.
    """
    try:
        response = requests.post(
            GO_SCRAPER_URL, 
            json={"urls": urls}, 
            timeout=20
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []
