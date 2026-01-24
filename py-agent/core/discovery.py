from serpapi import GoogleSearch
import os

def get_news_urls(topic, api_key=None):
    """
    Fetches news URLs for a given topic using SerpAPI with a balanced strategy.
    
    Args:
        topic (str): The search topic.
        api_key (str, optional): The SerpAPI key. Defaults to env var.
        
    Returns:
        list: A list of URLs found (targeting ~14 total, balanced).
    """
    if not api_key:
        api_key = os.getenv("SERP_API_KEY") or os.getenv("SERPAPI_KEY")
    
    if not api_key:
        print("Error: SERPAPI_KEY is missing.")
        return []

    # Two distinct queries to force coverage
    # Note: These domain lists are representative proxies to ensure we get *some* coverage from each side.
    # The agent will classify them for real later, but this seeding helps avoid 100% overlap.
    queries = [
        f"{topic} (site:cnn.com OR site:msnbc.com OR site:nytimes.com OR site:politico.com OR site:theguardian.com OR site:huffpost.com)", # Left/Center-Left
        f"{topic} (site:foxnews.com OR site:breitbart.com OR site:nypost.com OR site:dailywire.com OR site:washingtontimes.com OR site:nationalreview.com)" # Right/Center-Right
    ]
    
    collected_urls = []
    
    for q in queries:
        params = {
            "engine": "google_news",
            "q": q,
            "api_key": api_key,
            "gl": "us",
            "hl": "en"
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            news_results = results.get("news_results", [])
            
            # Take top 7 from each side
            side_urls = [item.get("link") for item in news_results if "link" in item]
            collected_urls.extend(side_urls[:7])
            
        except Exception as e:
            print(f"Error fetching news from SerpAPI for query '{q}': {e}")
            continue

    # Fallback: If we got nothing (strict queries failed), do a generic search
    if not collected_urls:
        print("DEBUG: Strict balanced search yielded 0 results. Falling back to generic search.")
        try:
            params = {
                "engine": "google_news",
                "q": topic,
                "api_key": api_key,
                "gl": "us",
                "hl": "en"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            news_results = results.get("news_results", [])
            collected_urls = [item.get("link") for item in news_results if "link" in item]
        except Exception as e:
            print(f"Error fetching news from SerpAPI (Fallback): {e}")

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for url in collected_urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
            
    return unique_urls[:14] # Cap at 14 as requested
