---
description: "Fork of langchain-ai/open_deep_research — autonomous deep research agent that runs parallel web searches across sub-agents and produces a comprehensive cited report."
tags: ["research", "deep-research", "report-generation", "web-search", "langgraph"]
authors:
  - name: Simon Guerrier
    account: simwar
repository: github:Simwar/open_deep_research
capabilities:
  - "Parallel web research using multiple concurrent sub-agents"
  - "Clarifying questions to scope research before starting"
  - "Comprehensive report generation with citations"
  - "Configurable search backends (Tavily, OpenAI, Anthropic native search)"
  - "Configurable research, summarization, and report models"
integrations:
  - "openai"
  - "anthropic"
  - "tavily"
---

Open Deep Research is a fully open-source autonomous research agent built on LangGraph. This is a fork of the original [open_deep_research](https://github.com/langchain-ai/open_deep_research) by LangChain AI. Give it any topic or question and it will scope the research (optionally asking clarifying questions), spin up parallel sub-agents to search the web, and synthesize findings into a well-structured, cited report.

**Example prompts:**
- "What are the latest developments in fusion energy?"
- "Compare the top vector database providers for production use"
- "Write a competitive analysis of the API management market"
- "Summarize the current state of AI regulation in the EU"

## Configuration

All settings are optional — sensible defaults are provided. Configure via deployment inputs:

| Input | Default | Description |
|-------|---------|-------------|
| `TAVILY_API_KEY` | — | Required when `SEARCH_API=tavily` (default) |
| `SEARCH_API` | `tavily` | Search backend: `tavily`, `openai`, `anthropic`, `none` |
| `RESEARCH_MODEL` | `openai:gpt-4.1` | Model used by research sub-agents |
| `FINAL_REPORT_MODEL` | `openai:gpt-4.1` | Model that writes the final report |
| `SUMMARIZATION_MODEL` | `openai:gpt-4.1-mini` | Model for summarizing raw search results |
| `COMPRESSION_MODEL` | `openai:gpt-4.1` | Model for compressing sub-agent findings |
| `MAX_CONCURRENT_RESEARCH_UNITS` | `5` | Number of parallel sub-agents (1–20) |
| `ALLOW_CLARIFICATION` | `true` | Ask a clarifying question before starting |

## Getting a Tavily API Key

Tavily is the default search backend. To get an API key:

1. Go to [app.tavily.com](https://app.tavily.com) and create a free account
2. After signing in, navigate to **API Keys** in the dashboard
3. Copy your API key and set it as the `TAVILY_API_KEY` deployment input

The free tier includes 1,000 searches/month. For higher usage, see [tavily.com/pricing](https://tavily.com/pricing).

> **Tip:** If you don't want to use Tavily, set `SEARCH_API` to `openai` or `anthropic` to use those providers' built-in search tools instead — no Tavily key needed.

## Limitations

- Research quality depends on the configured search API and model; Tavily + GPT-4.1 is the recommended default
- High concurrency settings may hit provider rate limits
