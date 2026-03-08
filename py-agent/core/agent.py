import os  # Standard library to interact with the operating system (e.g., checking environment variables).
from concurrent.futures import ThreadPoolExecutor, as_completed  # Tools to run multiple tasks at once (parallel processing) to speed things up.
from typing import List, Dict, Any  # Type hinting helpers to make the code easier to read and debug (e.g., defining what a list contains).
from langchain_groq import ChatGroq  # The specific library to talk to Groq's super-fast AI models.
from langchain_core.prompts import ChatPromptTemplate  # a tool to create structured "fill-in-the-blank" templates for sending to the AI.
from langchain_core.output_parsers import StrOutputParser  # A tool to clean up the AI's response and just get the text string.
from pydantic import BaseModel, Field  # Libraries for data validation; ensures the data we get matches what we expect.
from sqlalchemy.orm import Session  # Used to create a temporary connection "session" to our database.
from sqlalchemy import select  # A tool to write "SELECT" queries to find data in the database.
from core.database import init_db, AnalysisResult, get_db_engine  # Importing our own custom database setup and models from another file.

# This class defines the "shape" of the data we want the AI to give us back for each article.
class ArticleAnalysis(BaseModel):
    # We ask the AI to categorize the article's bias as specifically 'Left', 'Center', or 'Right'.
    bias: str = Field(description="Political bias: 'Left', 'Center', or 'Right'")
    # We ask the AI to provide a one-sentence summary.
    summary: str = Field(description="A one-sentence summary of the article")

# This is the main function that coordinates the entire AI analysis process.
# It takes a 'topic' (string) and a list of 'articles' (dictionaries) as input.
def run_full_analysis(topic: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Orchestrates the full analysis workflow:
    1. Classifies articles (Bias/Summary)
    2. Synthesizes narratives for Left/Right
    3. Detects omissions between narratives
    """
    
    # Run the function to make sure our database tables exist before we try to use them.
    init_db()
    
    # Initialize the AI Models we will use.
    
    # Model 1: "Maverick". We use this for writing the final long reports because it's good at synthesis.
    # temperature=0.3 means it's a little bit creative, but mostly focused.
    llm_synthesis = ChatGroq(model_name="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0.3)
    
    # Model 2: "Versatile" (Instance A). We use this powerful model to analyze individual articles.
    # temperature=0 means it is very strict and factual, effectively "0 creativity".
    llm_processing_a = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    
    # Model 3: "Versatile" (Instance B). We create a second instance just to separate the workload conceptually.
    llm_processing_b = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    # Chain 1: This is the setup for analyzing a single article.
    # We create a prompt template that tells the AI exactly how to act.
    classifier_prompt = ChatPromptTemplate.from_template(
        "Analyze the following article text with high precision. Determine its political bias (Left, Center, or Right) "
        "and provide a nuanced one-sentence summary that captures the core argument.\n\n"
        "1. **Bias Detection**: Look for framing, word choice, and omission. Use the domain name as a strong signal (e.g., Fox/Breitbart -> Right; CNN/MSNBC -> Left) but verify with the content.\n"
        "2. **Summary**: Extract the central thesis. Be concise but analytical.\n\n"
        "Article Text:\n{text}"  # {text} is where we will insert the actual article content later.
    )
    
    # We combine the prompt + the model + the expected output format (ArticleAnalysis) into a "chain".
    # ".with_structured_output" forces the AI to return JSON that matches our Class definition above.
    chain_a = classifier_prompt | llm_processing_a.with_structured_output(ArticleAnalysis)
    chain_b = classifier_prompt | llm_processing_b.with_structured_output(ArticleAnalysis)

    # Chain 2: This setup is for summarizing a whole group of articles (e.g., all Left-wing articles).
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
    # We create the synthesizer chain using the synthesis model.
    # StrOutputParser ensures we just get the text back, not a complex object.
    synthesizer_chain = synthesizer_prompt | llm_synthesis | StrOutputParser()

    # Chain 3: This is for the final "Omission Report" that compares both sides.
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
    # Create the final chain.
    omission_chain = omission_prompt | llm_synthesis | StrOutputParser()

    # --- Main execution logic starts here ---
    
    # Create a list to hold the final results of our analysis.
    results = []
    
    # Get the "engine" which is the main connection point to our database.
    engine = get_db_engine()
    
    # We need to filter the raw articles to make sure they are valid.
    valid_articles = []
    for article in articles:
        # Try to find the text of the article in various potential fields.
        text = article.get("content") or article.get("text") or str(article)
        # Only keep the article if it actually has text and is longer than 100 characters.
        if text and len(text) > 100: 
            valid_articles.append({"url": article.get("url"), "text": text})

    # To process faster, we split the articles into two batches to run on two models slightly out of sync.
    midpoint = len(valid_articles) // 2
    batch_a = valid_articles[:midpoint] 
    batch_b = valid_articles[midpoint:]
    
    # Print a debug message so we can see what's happening in the console.
    print(f"DEBUG: Processing {len(batch_a)} + {len(batch_b)} articles.")

    # A helper function to process a single article. This is what runs in parallel.
    def process_article(article, chain, model_name):
        # Step 1: Check if we have already analyzed this URL before (Caching).
        try:
            # Open a database session.
            with Session(engine) as session:
                # Ask the DB: "Do you have a row where the URL matches this article?"
                stmt = select(AnalysisResult).where(AnalysisResult.url == article.get("url"))
                cached_result = session.execute(stmt).scalar_one_or_none()
                
                # If we found a result and it has a summary, use it!
                if cached_result and cached_result.summary:
                    print(f"DEBUG: Cache Hit for {article.get('url')}")
                    # Update the topic if the user asked about something different this time.
                    if cached_result.topic != topic:
                        cached_result.topic = topic
                    # If the database was missing the full content text, save it now.
                    if not cached_result.content:
                        cached_result.content = article["text"]
                    # Save any changes to the DB.
                    session.commit()
                    # Return the cached result so we don't need to pay for an LLM call.
                    return ArticleAnalysis(bias=cached_result.bias_rating, summary=cached_result.summary)
        except Exception as e:
            # If the DB check fails, just print the error and continue to trying to analyze it fresh.
            print(f"DEBUG: Cache lookup failed: {e}")

        # Step 2: If not cached, run the analysis using the AI.
        try:
            print(f"DEBUG: Running Analysis ({model_name}) for {article.get('url')}")
            # Invoke the LangChain chain we created earlier.
            analysis = chain.invoke({"text": article["text"]})
            
            # Step 3: Save the new result to the database for next time.
            try:
                with Session(engine) as session:
                    # Check one more time if it exists (in case two threads tried to save it at once).
                    existing = session.execute(select(AnalysisResult).where(AnalysisResult.url == article.get("url"))).scalar_one_or_none()
                    if existing:
                        # Update existing entry.
                        existing.bias_rating = analysis.bias
                        existing.summary = analysis.summary
                        existing.content = article["text"]
                        existing.topic = topic
                    else:
                        # Create a new database entry.
                        db_entry = AnalysisResult(
                            topic=topic,
                            url=article.get("url", "unknown"),
                            bias_rating=analysis.bias,
                            summary=analysis.summary,
                            content=article["text"]
                        )
                        # Add it to the session.
                        session.add(db_entry)
                    # Commit (save) the transaction.
                    session.commit()
            except Exception as e:
                print(f"DEBUG: DB Save failed: {e}")
                
            return analysis
        except Exception as e:
            # If the AI fails to analyze, print the error and return None.
            print(f"DEBUG: LLM Analysis failed ({model_name}) for {article.get('url')}: {e}")
            return None

    # Step 4: Use a ThreadPool to run the 'process_article' function multiple times at once.
    # 'max_workers=5' means we run 5 articles parallelly.
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        
        # Add all articles from Batch A to the to-do list for the executor.
        for art in batch_a:
            futures.append(executor.submit(process_article, art, chain_a, "Versatile A"))
            
        # Add all articles from Batch B to the to-do list.
        for art in batch_b:
            futures.append(executor.submit(process_article, art, chain_b, "Versatile B"))
            
        # As each task finishes, collect the result.
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    # Step 5: Organize the results by bias (Left vs Center vs Right).
    grouped_summaries = {"Left": [], "Center": [], "Right": []}
    bias_counts = {"Left": 0, "Center": 0, "Right": 0}
    
    for res in results:
        # If the result is a known bias, add it to the correct list.
        if res.bias in grouped_summaries:
            grouped_summaries[res.bias].append(res.summary)
            bias_counts[res.bias] += 1
        else:
            # If the AI returned a weird bias name, just dump it in "Center" to be safe.
            grouped_summaries.setdefault("Center", []).append(res.summary)
            bias_counts.setdefault("Center", 0)
            bias_counts["Center"] += 1

    # Step 6: Generate the narrative summaries for each side.
    narratives = {}
    for bias in ["Left", "Right"]:
        summaries = grouped_summaries.get(bias, [])
        if summaries:
            # If we have articles, ask the AI to synthesize them into one story.
            narratives[bias] = synthesizer_chain.invoke({"bias": bias, "topic": topic, "summaries": "\n- ".join(summaries)})
        else:
            # If no articles, put a placeholder.
            narratives[bias] = "No articles found for this perspective."

    # Step 7: Generate the final comparison report.
    left_narrative = narratives.get("Left", "")
    right_narrative = narratives.get("Right", "")
    
    # Run the omission chain to compare the left and right narratives.
    omission_report = omission_chain.invoke({
        "topic": topic,
        "left_narrative": left_narrative,
        "right_narrative": right_narrative
    })

    # Return the final package of data to the API.
    return {
        "bias_counts": bias_counts,
        "narratives": narratives,
        "omission_report": omission_report
    }

# This function handles the "Chat with your Report" feature.
def run_chat_response(query: str, context_texts: List[str]) -> str:
    """
    Generates a response to a user query. 
    Prioritizes provided context for topic-specific questions, but allows general knowledge answers usually.
    """
    # Initialize a new AI model for chatting.
    llm_chat = ChatGroq(model_name="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.5)

    # Set the base rules for how the chatbot should behave.
    base_instruction = (
        "You are a helpful research assistant. "
        "Answer the user's question clearly and concisely. "
        "Use the provided 'Context' (which contains news analysis) to support your answer if the question relates to the analyzed topic. "
        "If the question is general (like 2+2) or unrelated to the context, answer it directly using your general knowledge, but state if the context was unhelpful.\n"
        "Do not include internal reasoning or tags in your response.\n\n"
    )

    # Prepare the context (the news we found).
    if not context_texts:
        # If no articles were passed in, just say so.
        full_context = "No specific articles analyzed yet."
    else:
        # Combine all the article texts into one big string.
        # We limit it to 50,000 characters so we don't crash the AI with too much text.
        full_context = "\n\n".join(context_texts)[:50000]

    # Create the prompt that sends the rules, the news context, and the user's question to the AI.
    prompt = ChatPromptTemplate.from_template(
        f"{base_instruction}"
        "Context:\n{context}\n\n"
        "User Question: {query}"
    )

    # Create the chain: Prompt -> Model -> Text Output.
    chain = prompt | llm_chat | StrOutputParser()
    
    # Run the chain and return the answer.
    return chain.invoke({"context": full_context, "query": query})
