"""
Backend API for the Parallax frontend.
Wraps the agent functionality so it can be called via REST.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import queue
import threading
from sqlalchemy import text

from core.scraper_client import fetch_articles, fetch_articles_with_progress, GO_SCRAPER_URL
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
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint to verify backend is online"""
    return {"message": "Parallax AI Agent API is running", "docs": "/docs"}


# Database setup
engine = get_db_engine()

# Data models
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
    # Optional: pass the generated report so chat knows what user is looking at
    left_narrative: Optional[str] = None
    right_narrative: Optional[str] = None
    overview: Optional[str] = None
    include_sources: Optional[bool] = False


class ChatResponse(BaseModel):
    answer: str


# API Endpoints
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
    Runs the full pipeline: Discovery -> Scraping -> Analysis
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
        # Step 1: Find relevant news sources
        urls = get_news_urls(topic, serp_key)
        
        if not urls:
            raise HTTPException(
                status_code=404, 
                detail="No relevant sources found for this topic"
            )
        
        # Step 2: Scrape article content
        articles = fetch_articles(urls)
        
        if not articles:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch article content. The scraper may be starting up—please try again in a minute."
            )
        
        # Step 3: Run the execution pipeline
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


def _run_analysis_stream(topic: str, serp_key: str, out_queue: queue.Queue) -> None:
    """Runs discovery -> scrape (with progress) -> analysis and puts SSE events into out_queue."""
    try:
        out_queue.put({"event": "progress", "phase": "discovery", "progress": 5, "message": "Finding sources..."})
        urls = get_news_urls(topic, serp_key)
        if not urls:
            out_queue.put({"event": "error", "detail": "No relevant sources found for this topic"})
            return
        out_queue.put({"event": "progress", "phase": "discovery", "progress": 15, "message": f"Found {len(urls)} sources"})

        def on_scrape_progress(current: int, total: int, articles_count: int) -> None:
            # Map scraping to 15–60% of total progress
            pct = 15 + int(45 * current / total) if total else 15
            out_queue.put({"event": "progress", "phase": "scraping", "progress": pct, "current": current, "total": total, "message": f"Reading article {current} of {total}"})

        out_queue.put({"event": "progress", "phase": "scraping", "progress": 15, "current": 0, "total": len(urls), "message": "Ingesting data..."})
        articles = fetch_articles_with_progress(urls, on_progress=on_scrape_progress)
        if not articles:
            out_queue.put({"event": "error", "detail": "Could not fetch article content. The scraper may be starting up—please try again in a minute."})
            return
        out_queue.put({"event": "progress", "phase": "scraping", "progress": 60, "current": len(urls), "total": len(urls), "message": "Scraping complete"})

        out_queue.put({"event": "progress", "phase": "analysis", "progress": 65, "message": "Synthesizing narratives..."})

        # Run analysis in a way that allows heartbeat progress updates
        analysis_done = threading.Event()
        analysis_result_holder = [None]
        analysis_error_holder = [None]

        def run_analysis_task():
            try:
                analysis_result_holder[0] = run_full_analysis(topic, articles)
            except Exception as e:
                analysis_error_holder[0] = e
            finally:
                analysis_done.set()

        analysis_thread = threading.Thread(target=run_analysis_task)
        analysis_thread.start()

        # Heartbeat: send progress updates every 3 seconds while analysis runs
        current_pct = 65
        analysis_messages = [
            "Classifying article bias...",
            "Processing with GPT-OSS 120B...",
            "Synthesizing left-wing narrative...",
            "Synthesizing right-wing narrative...",
            "Generating comprehensive overview...",
            "Detecting omissions between narratives...",
            "Cross-referencing perspectives...",
            "Finalizing analysis...",
        ]
        msg_index = 0
        while not analysis_done.wait(timeout=3.0):
            if current_pct < 92:
                current_pct += 3
                msg = analysis_messages[msg_index % len(analysis_messages)]
                msg_index += 1
                out_queue.put({"event": "progress", "phase": "analysis", "progress": current_pct, "message": msg})

        analysis_thread.join()

        if analysis_error_holder[0]:
            raise analysis_error_holder[0]

        analysis_results = analysis_result_holder[0]
        out_queue.put({"event": "progress", "phase": "analysis", "progress": 95, "message": "Almost done..."})

        bias_counts = analysis_results.get("bias_counts", {})
        narratives = analysis_results.get("narratives", {})
        sources_list = [{"url": a.get("url"), "title": a.get("title", ""), "source": a.get("source", "")} for a in articles if a.get("url")]
        result = {
            "success": True,
            "topic": topic,
            "bias_counts": {"Left": bias_counts.get("Left", 0), "Center": bias_counts.get("Center", 0), "Right": bias_counts.get("Right", 0)},
            "narratives": {"Left": narratives.get("Left", ""), "Right": narratives.get("Right", "")},
            "omission_report": analysis_results.get("omission_report", ""),
            "sources_count": sum(bias_counts.values()),
            "sources": sources_list,
        }
        out_queue.put({"event": "result", "data": result})
    except Exception as e:
        out_queue.put({"event": "error", "detail": str(e)})
    finally:
        out_queue.put(None)


def _sse_generate(topic: str, serp_key: str):
    q = queue.Queue()
    thread = threading.Thread(target=_run_analysis_stream, args=(topic, serp_key, q))
    thread.start()
    while True:
        item = q.get()
        if item is None:
            break
        yield f"data: {json.dumps(item)}\n\n"


@app.post("/api/analyze/stream")
async def analyze_topic_stream(request: AnalyzeRequest):
    """
    Streaming analysis: returns Server-Sent Events with progress, then final result.
    Event types: progress (phase, progress 0-100, message, current, total), result (data), error (detail).
    """
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    groq_key = os.getenv("GROQ_API_KEY")
    serp_key = os.getenv("SERP_API_KEY") or os.getenv("SERPAPI_KEY")
    if not groq_key or not serp_key:
        raise HTTPException(status_code=500, detail="API keys not configured (GROQ_API_KEY, SERP_API_KEY)")
    return StreamingResponse(
        _sse_generate(topic, serp_key),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_context(request: ChatRequest):
    """
    Chat endpoint. Uses provided report context, or falls back to DB content.
    """
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    try:
        # Priority 1: Use provided report context (narratives + overview)
        context_texts = []
        if request.left_narrative or request.right_narrative or request.overview:
            if request.left_narrative:
                context_texts.append(f"LEFT-WING PERSPECTIVE:\n{request.left_narrative}")
            if request.right_narrative:
                context_texts.append(f"RIGHT-WING PERSPECTIVE:\n{request.right_narrative}")
            if request.overview:
                context_texts.append(f"ANALYSIS OVERVIEW:\n{request.overview}")
            print(f"DEBUG: Using provided report context for topic: {topic}")
        
        # Determine if we should fetch additional source content from DB
        # Either because we have no context, OR because user requested include_sources
        fetch_db_content = (not context_texts) or request.include_sources
        
        if fetch_db_content:
            with engine.connect() as conn:
                # Get summaries and content for this topic
                stmt = text("""
                    SELECT bias_rating, summary, content 
                    FROM analysis_results 
                    WHERE LOWER(topic) = LOWER(:topic) 
                    AND (summary IS NOT NULL OR content IS NOT NULL)
                    ORDER BY timestamp DESC
                    LIMIT 20
                """)
                result = conn.execute(stmt, {"topic": topic})
                
                # If we already have report context and are just adding sources, be selective
                # to avoid duplicate info or overwhelming context window
                db_context_items = []
                for row in result:
                    bias, summary, content = row
                    item_text = ""
                    # If we just want sources to support the report
                    if request.include_sources:
                         # Append source content if available
                         if content:
                             item_text = f"SOURCE ARTICLE ({bias or 'Unknown Bias'}):\n{content[:2500]}"
                         elif summary:
                             item_text = f"SOURCE SUMMARY ({bias or 'Unknown Bias'}):\n{summary}"
                    else:
                        # Fallback mode (no report context)
                        if summary:
                            item_text = f"[{bias}] {summary}"
                        elif content:
                            item_text = content[:2000]
                    
                    if item_text:
                        db_context_items.append(item_text)
                
                # If appending to existing context, add a separator
                if context_texts and db_context_items:
                    context_texts.append("\n=== DETAILED SOURCE MATERIAL ===\n")
                    context_texts.extend(db_context_items)
                    print(f"DEBUG: Added {len(db_context_items)} source items from DB to context")
                elif not context_texts:
                     context_texts = db_context_items
                     print(f"DEBUG: Using DB context fallback for topic: {topic}, found {len(context_texts)} items")
        
        if not context_texts:
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
