# %%

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ClearToolUsesEdit,
    ContextEditingMiddleware,
    ModelCallLimitMiddleware,
    ModelFallbackMiddleware,
    SummarizationMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.prompts import load_prompt
from leann import LeannSearcher

load_dotenv(".env")


# Load system prompt from YAML file
system_prompt = load_prompt("prompts/system_prompt.yaml").format()
search_tool_description = load_prompt("prompts/system_prompt.yaml").format()

# VectorStore
searcher = LeannSearcher("vectorstore/langchain-docs.leann")

# AI Model
model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0.0,
)


# Tools
@tool("search", description=search_tool_description)
def search(query: str, top_k=5):
    results = searcher.search(query, top_k=top_k)

    # Format results as XML documents
    formatted_results = [
        f'<Document source="{r.metadata["source"]}">\n{r.text}\n</Document>'
        for r in results
    ]

    return "\n\n".join(formatted_results)


# RAG Chat Agent
# Note: When using LangGraph API, checkpointer is handled automatically by the platform
# and should not be specified here. The platform uses PostgreSQL for persistence.
agent = create_agent(
    model,
    tools=[search],
    system_prompt=system_prompt,
    middleware=[
        SummarizationMiddleware(
            model=model,
            max_tokens_before_summary=1200,
            messages_to_keep=5,
        ),
        ModelCallLimitMiddleware(
            thread_limit=None,
            run_limit=5,
            exit_behavior="end",
        ),
        ToolCallLimitMiddleware(
            thread_limit=None,
            run_limit=5,
        ),
        ContextEditingMiddleware(
            token_count_method="approximate",
            edits=[ClearToolUsesEdit()],
        ),
        ModelFallbackMiddleware("openai:gpt-4.1-mini"),
    ],
)
