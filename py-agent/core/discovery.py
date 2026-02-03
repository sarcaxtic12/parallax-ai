import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from serpapi import GoogleSearch

def generate_search_queries(topic: str, api_key: str = None) -> list:
    """
    Generates diverse search queries using Mixtral to ensure balanced coverage.
    """
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        print("Warning: GROQ_API_KEY missing, using simple fallback queries.")
        return [f'"{topic}" news', f'"{topic}" analysis']

    try:
        # Use 70B for high-quality query generation
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=api_key)
        
        prompt = ChatPromptTemplate.from_template(
            "You are a search expert. Generate 4 distinct Google News search queries to research the topic: '{topic}'.\n"
            "The goal is to find diverse perspectives (Left, Center, Right) and factual reporting.\n\n"
            "Rules:\n"
            "1. Query 1 (Neutral): '{topic} news'\n"
            "2. Query 2 (Left-Leaning): Use 'site:' with cnn.com, msnbc.com, nytimes.com, guardian.com. Example: '{topic} (site:cnn.com OR site:msnbc.com OR site:nytimes.com)'\n"
            "3. Query 3 (Right-Leaning): Use 'site:' with foxnews.com, nypost.com, washingtontimes.com, dailywire.com. Example: '{topic} (site:foxnews.com OR site:nypost.com OR site:dailywire.com)'\n"
            "4. Query 4 (Analysis): '{topic} analysis'\n"
            "5. Output ONLY the 4 queries, one per line.\n"
        )
        
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"topic": topic})
        
        queries = [q.strip() for q in result.strip().split('\n') if q.strip()]
        return queries[:4]
        
    except Exception as e:
        print(f"Error generating queries with LLM: {e}")
        return [topic, f"{topic} news", f"{topic} analysis"]

def get_news_urls(topic, api_key=None):
    """
    Fetches news URLs for a given topic using SerpAPI with LLM-generated queries.
    Target: ~18 Sources Total.
    """
    if not api_key:
        api_key = os.getenv("SERP_API_KEY") or os.getenv("SERPAPI_KEY")
    
    if not api_key:
        print("Error: SERPAPI_KEY is missing.")
        return []

    # Generate dynamic queries
    queries = generate_search_queries(topic)
    print(f"DEBUG: Generated Search Queries: {queries}")
    
    collected_urls = []
    
    # We want ~18 total from 4 queries. ~4-5 per query.
    for i, q in enumerate(queries):
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
            
            # Distribute limits: 5 sources per query => ~20 total, deduped to 18
            side_urls = [item.get("link") for item in news_results if "link" in item]
            collected_urls.extend(side_urls[:5])
            
        except Exception as e:
            print(f"Error fetching news from SerpAPI for query '{q}': {e}")
            continue

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for url in collected_urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
            
    return unique_urls[:18] # Cap at 18 as requested
