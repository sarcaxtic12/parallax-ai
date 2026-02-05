import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.database import init_db, AnalysisResult, get_db_engine

# Structure for the analysis output
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
    
    # Initialize LLMs
    
    # Synthesis Model (Maverick - Enhanced Synthesis, good for longer outputs)
    llm_synthesis = ChatGroq(model_name="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0.3)
    
    # Classification Model A (Llama 3.3 70B Versatile - High Quality)
    llm_processing_a = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    
    # Classification Model B
    llm_processing_b = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    # Chain 1: Determine bias and summary for each article
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

    # Chain 2: Synthesize narratives from clustered summaries
    synthesizer_prompt = ChatPromptTemplate.from_template(
        "You are an expert political analyst. Synthesize the **{bias}** perspective on: **'{topic}'**.\n\n"
        "**Source Summaries:**\n{summaries}\n\n"
        "**Instructions:**\n"
        "1. Write a single, focused paragraph (60-100 words) capturing the core {bias} viewpoint.\n"
        "2. Be SPECIFIC. Mention key arguments, concerns, or positions held by this side.\n"
        "3. If the summaries discuss related policy, economic, or social implications of '{topic}', include those angles.\n"
        "4. ONLY if the summaries are completely unrelated to '{topic}' (e.g., about sports when topic is politics), output: 'No significant reporting found from this perspective on this specific topic.'\n"
        "5. Output ONLY the paragraph, no preamble.\n"
    )
    synthesizer_chain = synthesizer_prompt | llm_synthesis | StrOutputParser()

    # Chain 3: Generate the final comparative report
    omission_prompt = ChatPromptTemplate.from_template(
        "You are a senior political analyst writing a balanced briefing on: **'{topic}'**.\n\n"
        "**Left-Wing Perspective:**\n{left_narrative}\n\n"
        "**Right-Wing Perspective:**\n{right_narrative}\n\n"
        "**Write a comprehensive analysis (600-900 words) that:**\n"
        "1. **Opens with substance**: Start with a key fact, statistic, or concrete event. NO generic openers like 'The topic of...' or 'There has been significant debate...'\n"
        "2. **Answers the question**: If '{topic}' is a question (e.g., 'Is X happening?'), provide a DIRECT ANSWER based on the evidence, then explain.\n"
        "3. **Compares perspectives**: Explain what each side emphasizes and WHY they frame it that way.\n"
        "4. **Identifies blind spots**: What does each side minimize or ignore?\n"
        "5. **Provides an objective assessment**: Based on the narratives, what's the most balanced conclusion?\n\n"
        "**Critical Rule**: If the narratives say 'No significant reporting found', acknowledge that the search didn't find strong coverage and explain what typical {topic} discourse looks like based on your knowledge. Do NOT claim you have no information.\n"
    )
    omission_chain = omission_prompt | llm_synthesis | StrOutputParser()

    # Main execution logic
    
    # Run classification on all articles (parallelized)
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
        # Check semantic cache first
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

        # Run analysis if not cached
        try:
            print(f"DEBUG: Running Analysis ({model_name}) for {article.get('url')}")
            # Add timeout/retry logic implicitly via LangChain or just try/except
            analysis = chain.invoke({"text": article["text"]})
            
            # Persist to DB
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

    # Use a threadpool to speed up processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        
        # Schedule Batch A
        for art in batch_a:
            futures.append(executor.submit(process_article, art, chain_a, "Versatile A"))
            
        # Schedule Batch B
        for art in batch_b:
            futures.append(executor.submit(process_article, art, chain_b, "Versatile B"))
            
        # Collect results
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

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

    # Synthesize narratives
    narratives = {}
    for bias in ["Left", "Right"]:
        summaries = grouped_summaries.get(bias, [])
        if summaries:
            narratives[bias] = synthesizer_chain.invoke({"bias": bias, "topic": topic, "summaries": "\n- ".join(summaries)})
        else:
            narratives[bias] = "No articles found for this perspective."

    # Run narrative gap analysis
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
