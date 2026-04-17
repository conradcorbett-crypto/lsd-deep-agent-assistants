"""Research Agent - Standalone script for LangGraph deployment.

This module creates a deep research agent with custom tools and prompts
for conducting web research with strategic thinking and context management.
"""

import os
import sys
from typing import Callable

# Ensure sibling packages (research_agent/) are importable
sys.path.insert(0, os.path.dirname(__file__))

from langchain.chat_models import init_chat_model
from langchain.agents.middleware import (
    dynamic_prompt,
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

from deep_agent.context import Context
from deep_agent.tools import get_tools
from langgraph.runtime import Runtime
from langchain.chat_models import init_chat_model


async def make_graph(runtime: Runtime[Context]):

    configurable = runtime.get("configurable", {})
    llm = configurable.get("model", "anthropic:claude-haiku-4-5")
    selected_tools = configurable.get("selected_tools", ["get_todays_date"])
    prompt = configurable.get("system_prompt", "You are a helpful AI assistant.")
    agent_name = configurable.get("name", "react_agent")

    # Route /memories/ to the persistent LangGraph store; everything else stays ephemeral.
    backend = lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    )

    graph = create_deep_agent(
        model=init_chat_model(llm),
        tools=get_tools(selected_tools),
        system_prompt=prompt,
        context_schema=Context,
        name=agent_name,
        memory=["/memories/AGENTS.md"],
        backend=backend,
    )

    return graph