# Parallax AI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Go](https://img.shields.io/badge/backend-Go-00ADD8.svg?logo=go&logoColor=white)
![Python](https://img.shields.io/badge/agent-Python-3776AB.svg?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/frontend-Next.js-black.svg?logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/container-Docker-2496ED.svg?logo=docker&logoColor=white)

> **Autonomous Narrative Intelligence & Media Bias Analysis Platform**

**Parallax AI** is a sophisticated research agent designed to see beyond the news cycle. By autonomously orchestrating a fleet of diverse microservices, it monitors global events, analyzes how different political spectrums frame the same story, and synthesizes a unified, factual perspective—bridging the "Parallax Gap" between conflicting narratives.

---

## 🔍 Visualizing the Truth

In today's fragmented media landscape, truth is often a casualty of framing. A single event can be reported in three diametrically opposite ways depending on the outlet's alignment. This phenomenon creates **"Parallax Gaps"**—blind spots where audiences are only shown half the picture.

**Parallax AI** was built to solve this information asymmetry. It doesn't just aggregate news; it *reads* and *understands* it.

The system acts as an autonomous digital analyst that:
1.  **Observes**: Constantly monitors live feeds for emerging topics.
2.  **Investigates**: Deploys high-concurrency scrapers to fetch full article text from Left, Center, and Right-leaning sources.
3.  **Comprehends**: Uses advanced Large Language Models (LLMs) to perform deep semantic analysis, identifying specific omissions, emotional loaded language, and narrative manipulation.
4.  **Synthesizes**: Generates a unified "Omission Report" that highlights exactly what each side left out, providing a holistic view of reality.

---

## ⚙️ Technical Architecture

Parallax AI is engineered as a modern, distributed system composed of specialized microservices, seamlessly orchestrated via Docker.

### 🧠 The Cognitive Core (Agent Orchestrator)
* **Stack**: Python, FastAPI, SQLAlchemy, AsyncIO
* **Role**: The brain of the operation. It manages the analysis workflow, maintains state, and interfaces with high-performance LLMs (via Groq/Llama 3) to process natural language at speed. It handles complex tasks like RAG (Retrieval-Augmented Generation) for the chat interface and structured output generation for bias metrics.

### ⚡ The Extraction Engine (High-Performance Scraper)
* **Stack**: Go (Golang), Gin Framework, Go-Readability
* **Role**: Speed and precision. Written in Go for raw performance, this microservice handles the heavy lifting of concurrent data fetching. It uses advanced DOM parsing to strip away ads, tracking scripts, and noise, delivering clean, machine-readable text to the core agent in milliseconds.

### 💎 The Interface (Liquid Glass UI)
* **Stack**: Next.js 14 (App Router), Tailwind CSS, Framer Motion
* **Role**: A "Vision OS" inspired experience. The frontend features a stunning "Liquid Glass" design aesthetic—dark, immersive, with glowing gradients and glassmorphism effects. It provides real-time visualization of data through the **Bias Meter**, **Narrative Cards**, and the **Omission Table**, making complex data intuitively understandable.

### 🗄️ The Memory (Data Layer)
* **Stack**: PostgreSQL
* **Role**: Persistence. Stores analysis results, vector embeddings for context-aware chat, and historical trends to track how narratives evolve over time.

---

## 🚀 Getting Started

Follow these steps to deploy the full system locally.

### Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.
*   API Keys for **Groq** (LLM Inference) and **SerpAPI** (Search & Discovery).

### Quick Start

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/parallax-ai.git
    cd parallax-ai
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    # Database
    POSTGRES_USER=parallax_user
    POSTGRES_PASSWORD=parallax_pass
    POSTGRES_DB=parallax_core

    # External APIs
    GROQ_API_KEY=your_groq_api_key_here
    SERP_API_KEY=your_serp_api_key_here

    # Service Links (Default for Docker Compose)
    DATABASE_URL=postgresql://parallax_user:parallax_pass@db:5432/parallax_core
    GO_SCRAPER_URL=http://go-scraper:8080/scrape
    ```

3.  **Launch the Fleet**
    Run the entire stack in detached mode:
    ```bash
    docker-compose up --build -d
    ```

4.  **Access the Platform**
    *   **Frontend UI**: [http://localhost:3000](http://localhost:3000)
    *   **Agent API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **Scraper API**: [http://localhost:8080](http://localhost:8080)

---

## 🔌 API Reference

The system exposes a RESTful API for integration or headless operation.

### Core Analysis
`POST /api/analyze`
Triggers a full discovery-scrape-analysis cycle on a specific topic.
```json
{
  "topic": "Global Economic Summit"
}
```

### Contextual Chat
`POST /api/chat`
Ask questions about previously analyzed topics. The agent uses RAG to answer from its knowledge base.
```json
{
  "topic": "Global Economic Summit",
  "query": "What did the left-leaning sources omit regarding the trade deal?"
}
```

### Historical Data
`GET /api/history`
Retrieves a list of recent analysis sessions and their timestamps.

---

## ☁️ Deployment

The project includes a `render.yaml` configuration for one-click deployment to **Render.com**. It automatically provisions:
*   A Managed PostgreSQL instance.
*   The Python Agent service.
*   The Go Scraper service.
*   The Next.js Frontend service.

---

*Built with precision and purpose.*
