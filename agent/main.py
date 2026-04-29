"""
Open Deep Research Agent — entry point

Environment variables (automatically injected by 'astro dev'):
  OPENAI_API_KEY       — injected by openai model provider
  ANTHROPIC_API_KEY    — injected by anthropic model provider
  TAVILY_API_KEY       — injected via inputs declaration
  GRPC_SERVER_ADDR     — injected by Astro messaging service

Optional configuration via env vars (maps to Configuration fields):
  SEARCH_API           — search backend: tavily | anthropic | openai | none (default: tavily)
  RESEARCH_MODEL       — model used by research sub-agents (default: openai:gpt-4.1)
  FINAL_REPORT_MODEL   — model that writes the final report (default: openai:gpt-4.1)
  SUMMARIZATION_MODEL  — model for summarizing raw search results (default: openai:gpt-4.1-mini)
  COMPRESSION_MODEL    — model for compressing sub-agent findings (default: openai:gpt-4.1)
  ALLOW_CLARIFICATION  — ask clarifying questions before researching (default: true)
  MAX_CONCURRENT_RESEARCH_UNITS — parallel sub-agent count (default: 5)
"""

from langchain_core.messages import AIMessage, HumanMessage
from open_deep_research.deep_researcher import deep_researcher
from astropods_adapter_langchain import serve
from astropods_adapter_core.types import AgentAdapter, StreamHooks, StreamOptions

SYSTEM_PROMPT = """
You are Open Deep Research, an autonomous research agent that produces comprehensive,
well-cited research reports on any topic.

Given a research question or topic, you will:
1. Optionally ask clarifying questions to scope the research
2. Delegate parallel research tasks to sub-agents using web search
3. Synthesize findings into a thorough, structured report with citations

You support multiple search backends (Tavily, OpenAI native search, Anthropic native search)
and can run many research sub-agents concurrently for fast, broad coverage.
""".strip()


def _extract_text(msg) -> str:
    content = msg.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


class DeepResearchAdapter:
    name = "open-deep-research"

    async def stream(self, prompt: str, hooks: StreamHooks, options: StreamOptions) -> None:
        try:
            async for chunk in deep_researcher.astream(
                {"messages": [HumanMessage(content=prompt)]},
                config={"configurable": {"thread_id": options.conversation_id}},
                stream_mode="updates",
            ):
                if "clarify_with_user" in chunk:
                    # Either a clarifying question (→ END) or a verification message (→ continue)
                    for msg in chunk["clarify_with_user"].get("messages", []):
                        if isinstance(msg, AIMessage):
                            text = _extract_text(msg)
                            if text:
                                hooks.on_chunk(text)

                elif "write_research_brief" in chunk:
                    hooks.on_status_update({
                        "status": "THINKING",
                        "custom_message": "Planning research scope...",
                    })

                elif "research_supervisor" in chunk:
                    hooks.on_status_update({
                        "status": "PROCESSING",
                        "custom_message": "Running research sub-agents...",
                    })

                elif "final_report_generation" in chunk:
                    hooks.on_status_update({
                        "status": "GENERATING",
                        "custom_message": "Writing final report...",
                    })
                    for msg in chunk["final_report_generation"].get("messages", []):
                        if isinstance(msg, AIMessage):
                            text = _extract_text(msg)
                            if text:
                                hooks.on_chunk(text)

            hooks.on_finish()

        except Exception as e:
            hooks.on_error(e)

    def get_config(self) -> dict:
        return {"system_prompt": SYSTEM_PROMPT, "tools": []}


serve(DeepResearchAdapter())
