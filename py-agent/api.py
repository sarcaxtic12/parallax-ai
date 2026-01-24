"""
FastAPI Backend API for Parallax AI Frontend
Wraps existing Python agent functions for REST consumption
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from sqlalchemy import text

from core.scraper_client import fetch_articles, GO_SCRAPER_URL
from core.agent import run_full_analysis, run_chat_response
from core.discovery import get_news_urls
from core.database import get_db_engine, AnalysisResult

app = FastAPI(
    title="Parallax AI API",
    description="Narrative Intelligence Analysis API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    # Allow all origins for the hackathon/demo context, but disable credentials to be spec-compliant
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint to verify backend is online"""
    return {"message": "Parallax AI Agent API is running", "docs": "/docs"}


# Global DB Engine
engine = get_db_engine()

# Request/Response Models
class AnalyzeRequest(BaseModel):
    topic: str


class AnalyzeStep(BaseModel):
    step: int
    message: str
    status: str  # "pending", "running", "complete", "error"


class BiasCount(BaseModel):
    Left: int = 0
    Center: int = 0
    Right: int = 0


class Narratives(BaseModel):
    Left: str = ""
    Right: str = ""


class AnalysisResponse(BaseModel):
    success: bool
    topic: str
    bias_counts: BiasCount
    narratives: Narratives
    omission_report: str
    sources_count: int
    sources: List[Dict[str, Any]] = []


class HistoryItem(BaseModel):
    topic: str
    last_run: str


class HistoryResponse(BaseModel):
    items: List[HistoryItem]


class HealthResponse(BaseModel):
    status: str
    database: str
    scraper: str


class ChatRequest(BaseModel):
    topic: str
    query: str


class ChatResponse(BaseModel):
    answer: str


# Endpoints
@app.on_event("startup")
async def startup_event():
    from core.database import init_db
    init_db()

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for container orchestration"""
    db_status = "ok"
    scraper_status = "ok"
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    
    # Check scraper (just verify env var exists)
    # Check scraper (verify URL is configured)
    scraper_url = GO_SCRAPER_URL
    if not scraper_url:
        scraper_status = "unknown"
    
    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status,
        scraper=scraper_status
    )


@app.get("/api/history", response_model=HistoryResponse)
async def get_history():
    """Fetch recent analysis topics from database"""
    try:
        history_query = text("""
            SELECT topic, MAX(timestamp) as last_run 
            FROM analysis_results 
            WHERE topic IS NOT NULL 
            GROUP BY topic 
            ORDER BY last_run DESC 
            LIMIT 15
        """)
        
        with engine.connect() as conn:
            result = conn.execute(history_query)
            items = [
                HistoryItem(
                    topic=row[0], 
                    last_run=row[1].isoformat() if row[1] else ""
                ) 
                for row in result
            ]
        
        return HistoryResponse(items=items)
    
    except Exception as e:
        # Return empty list on error (graceful degradation)
        print(f"History fetch error: {e}")
        return HistoryResponse(items=[])


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_topic(request: AnalyzeRequest):
    """
    Main analysis endpoint.
    Orchestrates: Discovery -> Scraping -> Analysis
    """
    topic = request.topic.strip()
    
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    serp_key = os.getenv("SERP_API_KEY") or os.getenv("SERPAPI_KEY")
    
    if not groq_key or not serp_key:
        raise HTTPException(
            status_code=500, 
            detail="API keys not configured (GROQ_API_KEY, SERP_API_KEY)"
        )
    
    try:
        # Step 1: Discover news URLs
        # Note: get_news_urls now runs balanced search (approx 14 urls)
        urls = get_news_urls(topic, serp_key)
        
        if not urls:
            raise HTTPException(
                status_code=404, 
                detail="No relevant sources found for this topic"
            )
        
        # Step 2: Scrape articles via Go microservice
        articles = fetch_articles(urls)
        
        if not articles:
            raise HTTPException(
                status_code=502, 
                detail="Failed to extract content from sources"
            )
        
        # Step 3: Run LLM analysis
        analysis_results = run_full_analysis(topic, articles)
        
        # Format response
        bias_counts = analysis_results.get("bias_counts", {})
        narratives = analysis_results.get("narratives", {})
        
        # Prepare sources list for frontend
        sources_list = []
        for art in articles:
            if art.get("url"):
                sources_list.append({
                    "url": art.get("url"),
                    "title": art.get("title", ""),
                    "source": art.get("source", ""),
                })
        
        return AnalysisResponse(
            success=True,
            topic=topic,
            bias_counts=BiasCount(
                Left=bias_counts.get("Left", 0),
                Center=bias_counts.get("Center", 0),
                Right=bias_counts.get("Right", 0)
            ),
            narratives=Narratives(
                Left=narratives.get("Left", ""),
                Right=narratives.get("Right", "")
            ),
            omission_report=analysis_results.get("omission_report", ""),
            sources_count=sum(bias_counts.values()),
            sources=sources_list
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_context(request: ChatRequest):
    """
    Chat endpoint. Fetches context from DB for the topic and answers using LLM.
    """
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    try:
        # Fetch content for the topic (from analysis_results)
        # We need the full text that was saved during analysis
        with engine.connect() as conn:
             # Basic query to get all 'content' for this topic
             stmt = text("SELECT content FROM analysis_results WHERE LOWER(topic) = LOWER(:topic) AND content IS NOT NULL")
             result = conn.execute(stmt, {"topic": topic})
             context_texts = [row[0] for row in result]
        
        if not context_texts:
             # Try partial match or just return helpful message
             print(f"DEBUG: No context found for topic: {topic}")
             return ChatResponse(answer="I couldn't find any analyzed articles for this topic in my database. Please run a new analysis first.")

        answer = run_chat_response(request.query, context_texts)
        return ChatResponse(answer=answer)

    except Exception as e:
        print(f"Chat error: {e}")
        error_msg = str(e)
        if "OperationalError" in error_msg:
             error_msg = "Database connection failed."
        raise HTTPException(status_code=500, detail=f"Chat failed: {error_msg}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
