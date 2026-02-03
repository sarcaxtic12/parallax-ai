# Parallax AI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)
![Go](https://img.shields.io/badge/backend-Go-00ADD8.svg?logo=go&logoColor=white)
![Python](https://img.shields.io/badge/agent-Python-3776AB.svg?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/frontend-Next.js-black.svg?logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/container-Docker-2496ED.svg?logo=docker&logoColor=white)

**Autonomous Narrative Intelligence & Media Bias Analysis Platform**

## Project Overview

Parallax AI is an advanced research tool designed to analyze media bias and narrative framing in real-time. By leveraging autonomous AI agents, the platform dissects conflicting news reports across the political spectrum—Left, Center, and Right—to identify omitted information and "Parallax Gaps" in coverage.

This project demonstrates a production-grade microservices architecture, integrating high-performance data collection with sophisticated natural language processing to deliver actionable insights into how the same event is portrayed differently by various outlets.

## Key Features

- **Autonomous Research Agent**: A Python-based orchestrator that intelligently searches, filters, and analyzes news sources.
- **High-Performance Scraper**: A dedicated Go microservice capable of concurrent, high-throughput content extraction.
- **Narrative Synthesis**: Uses Large Language Models (LLM) to synthesize distinct narratives and highlight omissions.
- **Conversational Interface**: An interactive chat system that retains context from analyzed reports, allowing users to interrogate the data deeply.
- **Production UI**: A modern, "Liquid Glass" diverse aesthetic built with Next.js and Tailwind CSS.

## The Workflow

Parallax AI automates the entire journey from topic discovery to deep narrative analysis.

### 1. Initiate Research
The user begins by querying a complex political or social topic. The system instantly aggregates diverse sources.

![Initiate Research](imgs/Start.jpg)

### 2. Narrative Synthesis
The autonomous agent parses dozens of articles, identifying distinct narrative threads and synthesizing them into a coherent overview.

![Narrative Synthesis](imgs/start-2.jpg)

### 3. Comprehensive Analysis & Reporting
The core of the platform. A dual-pane view presents a **Research Report** alongside a **Bias Meter**, visualizing the political lean of sources and summarizing the core arguments of each perspective.

| Research Report | Bias Analysis |
|:---:|:---:|
| ![Research Report](imgs/middle-1.jpg) | ![Bias Meter](imgs/middle-2.jpg) |

### 4. Conversational Deep Dive
Users can interact with the findings through a context-aware chat interface. The agent recalls specific details from the analysis to answer follow-up questions about omissions and framing.

![Conversational Deep Dive](imgs/Last.jpg)

## Technical Architecture

The system is built as a distributed microservices application, ensuring scalability and separation of concerns.

### Agent Orchestrator (Python / FastAPI)
The brain of the operation. It manages the research workflow, interfaces with LLMs (Llama 3 via Groq), and handles the synthesis logic. Python was selected for its robust ecosystem in AI and data processing.

### High-Performance Scraper (Go / Gin)
A specialized microservice for raw speed. Written in Go, it handles concurrent scraping, HTML cleaning, and text extraction. This separation prevents the heavy IO/CPU load of scraping from blocking the agent's reasoning capabilities.

### Frontend Interface (Next.js 14)
A reactive, server-side rendered UI built with Next.js App Router and Tailwind CSS. It features a custom "Liquid Glass" design system, real-time streaming updates, and a responsive layout optimized for data density.

### Data Persistence (PostgreSQL)
Stores analysis results for caching and historical context. This persistence layer allows the chat agent to "remember" the specific content of articles analyzed in previous sessions.

## Installation & Local Development

Run the full stack locally using Docker Compose.

**Prerequisites**: [Docker Desktop](https://www.docker.com/products/docker-desktop/), [Groq API Key](https://console.groq.com/), [SerpAPI Key](https://serpapi.com/).

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/parallax-ai.git
   cd parallax-ai
   ```

2. **Configure Environment**
   Create a `.env` file in the root directory:
   ```ini
   GROQ_API_KEY=your_groq_key
   SERP_API_KEY=your_serp_key
   ```

3. **Start the Application**
   ```bash
   docker-compose up --build
   ```

4. **Access**
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Deployment

The project is configured for seamless deployment on platform-as-a-service providers like Render.

- **`render.yaml` included**: Defines all services (Web, Workers, DB) as infrastructure-as-code.
- **Auto-Deploy**: Configured to automatically build and deploy upon pushing to the `main` branch.

---
*Designed & Developed by Hyder Ahmed | © 2026 All Rights Reserved*
