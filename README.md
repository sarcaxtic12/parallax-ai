# Parallax AI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)
![Go](https://img.shields.io/badge/backend-Go-00ADD8.svg?logo=go&logoColor=white)
![Python](https://img.shields.io/badge/agent-Python-3776AB.svg?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/frontend-Next.js-black.svg?logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/container-Docker-2496ED.svg?logo=docker&logoColor=white)

**Autonomous Narrative Intelligence & Media Bias Analysis Platform**

## Technical Highlights

*   ** Architecture**: Event-driven Microservices (Python Agent + Go Scraper)
*   ** AI Model**: Llama 3 70B via Groq (Low-latency inference)
*   ** Performance**: Real-time concurrent scraping & streaming analysis responses
*   ** Frontend**: Next.js 14 App Router with Server-Sent Events (SSE)
*   ** Data**: PostgreSQL with semantic caching for context retention

## Project Overview

Parallax AI addresses the challenge of media bias by autonomously analyzing how different news outlets frame the same event. In an era of fragmented information, this tool serves as an automated researcher that aggregates dozens of sources from across the political spectrum to identify "Parallax Gaps" or key factual omissions between narratives.

The system is engineered as a production-grade distributed application. It leverages a high-performance Go microservice for rapid data extraction, ensuring the Python-based AI agent receives context without bottlenecking. This architecture allows for deep narrative synthesis that goes beyond simple summarization, offering users a comparative analysis of Left, Center, and Right perspectives.

## System Workflow & Demo

The application follows a linear research pipeline, transforming raw queries into structured intelligence.

### 1. Initiate Research
The entry point is a search interface designed for complex social and political queries.

![Initiate Research](imgs/Start.jpg)

### 2. Autonomous Synthesis
The system executes a multi-step chain of thought: discovering sources, scraping content in parallel, and synthesizing distinct narrative threads.

![Narrative Synthesis](imgs/start-2.jpg)

### 3. Deep Analysis Report
The findings are presented in a comprehensive dashboard. This research report deconstructs the core arguments of each political side and visualizes the aggregate bias of the sources used.

![Research Report](imgs/middle-1.jpg)

![Bias Analysis](imgs/middle-2.jpg)

### 4. Context-Aware Chat
Users can interrogate the data through a conversational interface. The agent retains the full context of the generated report, enabling it to answer specific questions about source credibility, tone, and omitted facts.

![Conversational Deep Dive](imgs/Last.jpg)

## Technical Architecture

The platform uses a microservices strategy to optimize for both speed and reasoning capabilities.

### Agent Orchestrator (Python / FastAPI)
Python functions as the control plane, managing the logic workflow and interfacing with the LLM providers. It handles the "thinking" tasks, such as bias classification, narrative synthesis, and context management for the chat system.

### High-Performance Scraper (Go / Gin)
To handle the IO-intensive task of web scraping, a dedicated Go microservice processes concurrent requests. It cleanses HTML, removes boilerplate, and extracts semantic text, delivering clean data to the agent significantly faster than synchronous Python solutions.

### Frontend Interface (Next.js 14)
The user interface is a "Liquid Glass" design built with Tailwind CSS and Framer Motion. It prioritizes data density and readability. The application uses Server-Sent Events (SSE) to stream the analysis progress and results in real-time, ensuring a responsive user experience even during heavy processing.

### Data Persistence (PostgreSQL)
PostgreSQL handles the persistence of analysis results and source metadata. This allows the system to cache expensive LLM operations and provides the necessary historical context for the chat agent to function effectively across sessions.

## Installation & Deployment

The system is containerized with Docker for consistent deployment across environments.

**Prerequisites**: [Docker Desktop](https://www.docker.com/products/docker-desktop/), [Groq API Key](https://console.groq.com/), [SerpAPI Key](https://serpapi.com/).

### Local Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/parallax-ai.git
    cd parallax-ai
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    GROQ_API_KEY=your_groq_key
    SERP_API_KEY=your_serp_key
    ```

3.  **Start the Application**
    ```bash
    docker-compose up --build
    ```
    Access the frontend at [http://localhost:3000](http://localhost:3000).

### Production Deployment

The repository includes a `render.yaml` infrastructure-as-code definition. It allows for one-click deployment to Render, automatically provisioning the Web Services (Frontend, Agent, Scraper) and the managed PostgreSQL database.

---
*Designed & Developed by Hyder Ahmed | © 2026 All Rights Reserved*
