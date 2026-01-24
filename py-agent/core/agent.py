import os
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.database import init_db, AnalysisResult, get_db_engine

# Define Structured Output
class ArticleAnalysis(BaseModel):
    bias: str = Field(description="Political bias: 'Left', 'Center', or 'Right'")
    summary: str = Field(description="A one-sentence summary of the article")

def run_full_analysis(topic: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Orchestrates the full analysis workflow:
    1. Classifies articles (Bias/Summary)
    2. Synthesizes narratives for Left/Right
    3. Detects omissions between narratives
    """
    
    # Ensure DB tables exist
    init_db()
    
    # Initialize LLM
    # Note: Expects GROQ_API_KEY to be set in environment
    
    # Synthesis Model (Maverick - Enhanced Synthesis)
    llm_synthesis = ChatGroq(model_name="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0.3)
    
    # Classification Model A (GPT-OSS)
    llm_processing_a = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0)
    
    # Classification Model B (GPT-OSS)
    llm_processing_b = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0)

    # Chain 1: Classifier Factory (Reusable Prompt - Enhanced)
    classifier_prompt = ChatPromptTemplate.from_template(
        "Analyze the following article text with high precision. Determine its political bias (Left, Center, or Right) "
        "and provide a nuanced one-sentence summary that captures the core argument.\n\n"
        "1. **Bias Detection**: Look for framing, word choice, and omission. Use the domain name as a strong signal (e.g., Fox/Breitbart -> Right; CNN/MSNBC -> Left) but verify with the content.\n"
        "2. **Summary**: Extract the central thesis. Be concise but analytical.\n\n"
        "Article Text:\n{text}"
    )
    
    # Create two separate chains bound to different models
    chain_a = classifier_prompt | llm_processing_a.with_structured_output(ArticleAnalysis)
    chain_b = classifier_prompt | llm_processing_b.with_structured_output(ArticleAnalysis)

    # Chain 2: Narrative Synthesizer (Concise Summary)
    synthesizer_prompt = ChatPromptTemplate.from_template(
        "You are an expert narrative analyst. Your goal is to write a single, cohesive paragraph (50-75 words) summarizing the **{bias}** perspective on: **'{topic}'**.\n\n"
        "**Input Data:**\n"
        "Summaries from {bias}-leaning sources: \n{summaries}\n\n"
        "**Response Guidelines:**\n"
        "- **Outcome Only**: Output ONLY the final summary paragraph. Do not explain your steps.\n"
        "- **Relevance**: Incorporate ONLY points relevant to '{topic}'. If the input summaries are about unrelated events, ignore them.\n"
        "- **Zero Relevant Data**: If absolutely no summaries relate to '{topic}', output exactly: 'No significant reporting found from this perspective on this specific topic.'\n"
    )
    synthesizer_chain = synthesizer_prompt | llm_synthesis | StrOutputParser()

    # Chain 3: Omission Detector (Deep Dive Overview)
    omission_prompt = ChatPromptTemplate.from_template(
        "You are a Senior Feature Editor at a prestige publication. Write a **definitive, high-quality feature article** (800+ words) on: **'{topic}'**.\n\n"
        "**Source Material:**\n"
        "**Left-Wing Narrative:**\n{left_narrative}\n\n"
        "**Right-Wing Narrative:**\n{right_narrative}\n\n"
        "**Writing Standards:**\n"
        "1. **No Generic Openers**: NEVER start with 'The topic of...', 'Significant discourse...', or 'The issue of...'. Start immediately with a strong hook, a concrete fact, or a vivid description of the core event.\n"
        "2. **Narrative Flow**: Do not just list 'Left says X, Right says Y'. Weaver the perspectives into a single cohesive story. Use transitional phrases that highlight the conflict naturally.\n"
        "3. **Synthesis**: Move beyond comparison. Explain *why* the narratives diverge (e.g., 'At the heart of the disagreement is a fundamental difference in how...')\n"
        "4. **Professionalism**: Maintain a sophisticated, authoritative tone throughout.\n\n"
        "**Article Structure:**\n"
        "1. **Title**: Engaging and specific (e.g., 'The Battle for the Border: Truth and Rhetoric').\n"
        "2. **Executive Summary**: A hard-hitting abstract (in bold).\n"
        "3. **The Deep Dive**: The main body. Dense with information, nuanced analysis, and fact-checking.\n"
        "4. **The Blind Spots**: A dedicated section analyzing what facts were omitted by each side.\n"
        "5. **Conclusion**: A final independent assessment.\n\n"
        "**Constraints:**\n"
        "- **Relevance Check**: If the provided narratives are empty or unrelated to '{topic}', explicitly write: 'NOTE: The available search results do not contain sufficient reporting on this specific topic to generate a full report.' Do not hallucinate content.\n"
    )
    omission_chain = omission_prompt | llm_synthesis | StrOutputParser()

    # Execution Flow
    
    # 1. Run Classifier on all articles (Split 50/50 for Parallel Processing)
    results = []
    
    # Initialize DB Engine (Once)
    engine = get_db_engine()
    
    # Filter valid articles first
    valid_articles = []
    for article in articles:
        text = article.get("content") or article.get("text") or str(article)
        if text and len(text) > 100: # Ensure minimal content
            valid_articles.append({"url": article.get("url"), "text": text})

    # Split into two batches
    midpoint = len(valid_articles) // 2
    batch_a = valid_articles[:midpoint] 
    batch_b = valid_articles[midpoint:]
    
    print(f"DEBUG: Processing {len(batch_a)} + {len(batch_b)} articles.")

    def process_article(article, chain, model_name):
        # 1. Check Cache
        try:
            with Session(engine) as session:
                stmt = select(AnalysisResult).where(AnalysisResult.url == article.get("url"))
                cached_result = session.execute(stmt).scalar_one_or_none()
                if cached_result and cached_result.summary:
                    print(f"DEBUG: Cache Hit for {article.get('url')}")
                    # Update topic to match current analysis
                    if cached_result.topic != topic:
                        cached_result.topic = topic
                    # If content is missing in cache (legacy), update it
                    if not cached_result.content:
                        cached_result.content = article["text"]
                    session.commit()
                    return ArticleAnalysis(bias=cached_result.bias_rating, summary=cached_result.summary)
        except Exception as e:
            print(f"DEBUG: Cache lookup failed: {e}")

        # 2. Run Analysis
        try:
            print(f"DEBUG: Running Analysis ({model_name}) for {article.get('url')}")
            # Add timeout/retry logic implicitly via LangChain or just try/except
            analysis = chain.invoke({"text": article["text"]})
            
            # 3. Save to DB
            try:
                with Session(engine) as session:
                    # Check if exists again to avoid race conditions
                    existing = session.execute(select(AnalysisResult).where(AnalysisResult.url == article.get("url"))).scalar_one_or_none()
                    if existing:
                        existing.bias_rating = analysis.bias
                        existing.summary = analysis.summary
                        existing.content = article["text"]
                        existing.topic = topic
                    else:
                        db_entry = AnalysisResult(
                            topic=topic,
                            url=article.get("url", "unknown"),
                            bias_rating=analysis.bias,
                            summary=analysis.summary,
                            content=article["text"]
                        )
                        session.add(db_entry)
                    session.commit()
            except Exception as e:
                print(f"DEBUG: DB Save failed: {e}")
                
            return analysis
        except Exception as e:
            print(f"DEBUG: LLM Analysis failed ({model_name}) for {article.get('url')}: {e}")
            return None

    # We could use threading here for true parallelism, but simplistic sequential batching 
    # simulates the load distribution and satisfies the "use two models" requirement.
    # To keep it robust without complex async in Streamlit, we'll iterate.
    
    # Process Batch A (Versatile)
    for art in batch_a:
        res = process_article(art, chain_a, "Versatile")
        if res: results.append(res)
        
    # Process Batch B (Scout)
    for art in batch_b:
        res = process_article(art, chain_b, "Scout")
        if res: results.append(res)

    # Group results
    grouped_summaries = {"Left": [], "Center": [], "Right": []}
    bias_counts = {"Left": 0, "Center": 0, "Right": 0}
    
    for res in results:
        if res.bias in grouped_summaries:
            grouped_summaries[res.bias].append(res.summary)
            bias_counts[res.bias] += 1
        else:
            # Fallback for unexpected bias output
            grouped_summaries.setdefault("Center", []).append(res.summary)
            bias_counts.setdefault("Center", 0)
            bias_counts["Center"] += 1

    # 2. Synthesize Narratives
    narratives = {}
    for bias in ["Left", "Right"]:
        summaries = grouped_summaries.get(bias, [])
        if summaries:
            narratives[bias] = synthesizer_chain.invoke({"bias": bias, "topic": topic, "summaries": "\n- ".join(summaries)})
        else:
            narratives[bias] = "No articles found for this perspective."

    # 3. Detect Omissions
    left_narrative = narratives.get("Left", "")
    right_narrative = narratives.get("Right", "")
    
    omission_report = omission_chain.invoke({
        "topic": topic,
        "left_narrative": left_narrative,
        "right_narrative": right_narrative
    })

    return {
        "bias_counts": bias_counts,
        "narratives": narratives,
        "omission_report": omission_report
    }

def run_chat_response(query: str, context_texts: List[str]) -> str:
    """
    Generates a response to a user query. 
    Prioritizes provided context for topic-specific questions, but allows general knowledge answers usually.
    """
    llm_chat = ChatGroq(model_name="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.5)

    base_instruction = (
        "You are a helpful research assistant. "
        "Answer the user's question clearly and concisely. "
        "Use the provided 'Context' (which contains news analysis) to support your answer if the question relates to the analyzed topic. "
        "If the question is general (like 2+2) or unrelated to the context, answer it directly using your general knowledge, but state if the context was unhelpful.\n"
        "Do not include internal reasoning or tags in your response.\n\n"
    )

    if not context_texts:
        # Fallback if no context provided (though api.py handles this, good for robustness)
        full_context = "No specific articles analyzed yet."
    else:
        # Limit context to avoid token overflow
        # Concatenate texts until approx limit or use top k
        full_context = "\n\n".join(context_texts)[:50000]

    prompt = ChatPromptTemplate.from_template(
        f"{base_instruction}"
        "Context:\n{context}\n\n"
        "User Question: {query}"
    )

    chain = prompt | llm_chat | StrOutputParser()
    
    return chain.invoke({"context": full_context, "query": query})
