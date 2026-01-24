# Parallax AI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Go](https://img.shields.io/badge/backend-Go-00ADD8.svg?logo=go&logoColor=white)
![Python](https://img.shields.io/badge/agent-Python-3776AB.svg?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/frontend-Next.js-black.svg?logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/container-Docker-2496ED.svg?logo=docker&logoColor=white)

**Autonomous Narrative Intelligence & Media Bias Analysis Platform**

## Project Overview

Parallax AI is a research tool designed to analyze media bias in real time. The goal of this project is to address the issue of "Parallax Gaps" where different news outlets report conflicting facts about the same event depending on their political alignment. Instead of just reading one source, this system uses an AI agent to read articles from Left, Center, and Right leaning sources to find out what information is being omitted by each side.

The system works by automating the entire research process. It monitors news feeds, downloads the article content, and uses Large Language Models (LLMs) to analyze the text. The final output is a report that highlights the differences in framing and facts across the political spectrum.

## Technical Architecture

This project is built as a distributed system using Docker. I chose to use a microservices architecture to handle the different requirements of scraping and analysis.

### Agent Orchestrator (Python)
The core logic is written in Python using FastAPI. This services acts as the controller. It manages the workflow and connects to the LLM (using Groq and Llama 3) to perform the text analysis. I used Python here because of its strong support for AI and data processing libraries.

### High Performance Scraper (Go)
For the web scraper, I used Go (Golang) with the Gin framework. Scrapers need to be fast and handle many requests at once, so Go was a better choice than Python for this specific component. It fetches the HTML, cleans it up to remove ads and scripts, and returns just the main text of the article.

### Frontend Interface (Next.js)
The user interface is built with Next.js 14 and Tailwind CSS. It is designed to look modern and clean, using a "Liquid Glass" theme. It communicates with the backend API to display the "Bias Meter" and other visualizations that help users understand the data.

### Database (PostgreSQL)
I am using PostgreSQL to store all the analysis results. It handles both the relational data for the reports and the vector data if needed for search context.

## How to Run Locally

You will need Docker Desktop installed to run this project. You also need API keys for Groq and SerpAPI.

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/parallax-ai.git
   cd parallax-ai
   ```

2. **Set up the environment variables**
   Create a file named `.env` in the root folder and add your keys:
   ```ini
   POSTGRES_USER=parallax_user
   POSTGRES_PASSWORD=parallax_pass
   POSTGRES_DB=parallax_core
   GROQ_API_KEY=your_groq_key
   SERP_API_KEY=your_serp_key
   DATABASE_URL=postgresql://parallax_user:parallax_pass@db:5432/parallax_core
   GO_SCRAPER_URL=http://go-scraper:8080/scrape
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build -d
   ```

4. **Open the application**
   *   The frontend will be running at `http://localhost:3000`.
   *   The API documentation is available at `http://localhost:8000/docs`.

## API Endpoints

If you want to use the API directly, here are the main endpoints:

*   **POST /api/analyze**
    This starts the analysis for a given topic. You need to send a JSON body with the "topic" key.
    ```json
    {
      "topic": "Global Economic Summit"
    }
    ```

*   **POST /api/chat**
    This allows you to ask questions about the analyzed data.
    ```json
    {
      "topic": "Global Economic Summit",
      "query": "What did the left-leaning sources omit?"
    }
    ```

*   **GET /api/history**
    This returns a list of past analyses.

## Deployment

The project is configured to run on Render using the `render.yaml` file. It sets up the database and all three services automatically.

