# Deep Agent Assistants

A walkthrough of deploying a configurable Deep Agent to LangSmith Deployments and using the LangGraph SDK to create and manage multiple assistant configurations on top of a single deployed graph.

## Overview

This repo demonstrates a core LangSmith pattern: **one deployed graph, many assistants**. The `deep_agent` graph exposes configurable parameters (model, system prompt, tools) so you can create distinct assistant personas — each with their own behavior, tool access, and long-term memory — without redeploying.

## Prerequisites

- Python 3.11+
- A [LangSmith](https://smith.langchain.com) account with API access
- An [Anthropic](https://console.anthropic.com) API key (for Claude models)
- A [Tavily](https://tavily.com) API key (for research tools)

## Environment Variables

Create a `.env` file in the root of the repo:

```
LANGSMITH_API_KEY=your_langsmith_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Deployment

You have two options to run the agent:

### Option 1 — Local development with LangGraph Dev

```bash
uv sync
uv run langgraph dev
```

This starts a local LangGraph server at `http://localhost:2024`. Use this URL in the notebook client setup.

### Option 2 — LangSmith Cloud Deployment

1. Push this repo to GitHub
2. In LangSmith, go to **Deployments** and create a new deployment
3. Connect your GitHub repo — LangSmith will build and deploy the graph automatically
4. Copy the deployment URL from the LangSmith UI

The `langgraph.json` file tells LangSmith which graphs to deploy:

```json
{
  "graphs": {
    "agent": "./src/deep_research/agent.py:agent",
    "deep_agent": "./src/deep_agent/agent.py:make_graph"
  }
}
```

## Notebook Walkthrough

Once the agent is deployed (locally or in the cloud), open `notebooks/assistant_test.ipynb` and work through the cells in order:

### 1. Connect to the deployed graph

Update the `url` in the client setup cell to point to your deployment (local or cloud):

```python
client = get_client(
    url="https://your-deployment-url.us.langgraph.app",
    api_key=os.environ["LANGSMITH_API_KEY"],
)
```

### 2. Create assistants

Each assistant is a named configuration on top of the `deep_agent` graph. You can customize:

- **`system_prompt`** — the assistant's persona and behavior
- **`model`** — the LLM to use (e.g. `anthropic:claude-haiku-4-5`)
- **`selected_tools`** — which tools the assistant has access to
- **`name`** — display name for the assistant

```python
assistant = await client.assistants.create(
    graph_id="deep_agent",
    config={
        "configurable": {
            "system_prompt": "You are a helpful AI assistant. Always reply in the voice of a pirate.",
            "model": "anthropic:claude-haiku-4-5",
            "selected_tools": ["get_todays_date", "advanced_research"],
            "name": "Pirate"
        }
    },
    name="Pirate",
)
```

Available tools:

| Tool | Description |
|------|-------------|
| `get_todays_date` | Returns the current date |
| `advanced_research` | Deep web research via Tavily (10 results) |
| `basic_research` | Quick web search via Tavily (5 results) |
| `finance_research` | Yahoo Finance news by ticker symbol |
| `langchain_docs` | Search LangChain documentation via MCP |

### 3. Seed assistant memory

Each assistant can have a persistent `AGENTS.md` file stored in the LangGraph store. This file is loaded at startup and scopes the assistant's long-term memory to its `assistant_id`. The notebook seeds each assistant's memory from files in `src/assistants/`:

```
src/assistants/
├── content-writer/AGENTS.md   # Persona instructions for the Pirate assistant
└── mcp-docs-agent/AGENTS.md   # Persona instructions for the Cowboy assistant
```

### 4. Stream a response

The final cells create a thread, send a message to an assistant, and stream the response token-by-token using `stream_mode="messages"`.

## Project Structure

```
.
├── langgraph.json                  # Graph entrypoints for deployment
├── pyproject.toml                  # Dependencies
├── notebooks/
│   └── assistant_test.ipynb        # Main walkthrough notebook
└── src/
    ├── assistants/
    │   ├── content-writer/AGENTS.md
    │   └── mcp-docs-agent/AGENTS.md
    └── deep_agent/
        ├── agent.py                # Graph definition (make_graph)
        ├── context.py              # Configurable assistant parameters
        └── tools.py                # Custom tools
```
