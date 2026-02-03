import requests
import os
import time
from typing import List, Dict, Any

GO_SCRAPER_HOST = os.getenv("GO_SCRAPER_HOST", "localhost")
GO_SCRAPER_PORT = os.getenv("GO_SCRAPER_PORT", "8080")
# Render sets RENDER=true; free tier has no private DNS, so use public URL when host has no domain.
_on_render = os.getenv("RENDER", "").lower() in ("1", "true", "yes")
_has_domain = "." in GO_SCRAPER_HOST and "onrender.com" in GO_SCRAPER_HOST

if os.getenv("GO_SCRAPER_URL"):
    GO_SCRAPER_URL = os.getenv("GO_SCRAPER_URL")
elif _has_domain:
    GO_SCRAPER_URL = f"https://{GO_SCRAPER_HOST}/scrape"
elif _on_render and GO_SCRAPER_HOST and "." not in GO_SCRAPER_HOST:
    # Short hostname on Render (e.g. scraper or scraper-xxxx) -> use public HTTPS URL
    GO_SCRAPER_URL = f"https://{GO_SCRAPER_HOST}.onrender.com/scrape"
else:
    GO_SCRAPER_URL = f"http://{GO_SCRAPER_HOST}:{GO_SCRAPER_PORT}/scrape"

def _source_from_url(url: str) -> str:
    """Derive a short source name from URL for display."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc or url
    except Exception:
        return url or ""


def fetch_articles(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches article content from the Go scraping service.
    Uses longer timeout and retries with backoff to handle Render free-tier cold start.
    Returns only successfully scraped articles (status=success) with content.
    """
    max_retries = 4
    timeout_seconds = 120  # Cold start on Render can take 50+ seconds
    backoff = [0, 5, 15, 25]  # Wait before each attempt (first immediate, then 5s, 15s, 25s)

    for attempt in range(max_retries):
        if backoff[attempt] > 0:
            time.sleep(backoff[attempt])
        try:
            print(f"DEBUG: Calling Scraper at {GO_SCRAPER_URL} (Attempt {attempt+1}/{max_retries})...")
            response = requests.post(
                GO_SCRAPER_URL,
                json={"urls": urls},
                timeout=timeout_seconds,
            )
            response.raise_for_status()

            data = response.json()
            if not data:
                print(f"DEBUG: Scraper returned empty list on attempt {attempt+1}")
                continue

            # Go scraper returns [{url, title, content, status}, ...]; keep only success with content
            articles = []
            for item in (data if isinstance(data, list) else []):
                if item.get("status") != "success":
                    continue
                content = (item.get("content") or "").strip()
                if not content or len(content) < 100:
                    continue
                articles.append({
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "content": content,
                    "source": _source_from_url(item.get("url", "")),
                })
            if articles:
                return articles
            print(f"DEBUG: No articles with valid content on attempt {attempt+1} (all failed or empty).")
        except requests.exceptions.Timeout as e:
            print(f"DEBUG: Scraper timeout (Attempt {attempt+1}): {e}")
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Scraper request error (Attempt {attempt+1}): {e}")
        except Exception as e:
            print(f"DEBUG: Scraper error (Attempt {attempt+1}): {e}")

    print("DEBUG: Scraper failed after max retries.")
    return []
