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


# # All available custom tool names — used to distinguish from deep agent built-ins
# CUSTOM_TOOL_NAMES = {"finance_research", "advanced_research", "basic_research", "get_todays_date"}

# # Model
# model = init_chat_model(model="anthropic:claude-haiku-4-5")


# @dynamic_prompt
# def context_system_prompt(request: ModelRequest) -> str:
#     """Inject the assistant's system prompt from context."""
#     ctx = request.runtime.context or Context()
#     return ctx.system_prompt


# @wrap_model_call
# def filter_tools_by_context(
#     request: ModelRequest,
#     handler: Callable[[ModelRequest], ModelResponse],
# ) -> ModelResponse:
#     """Only pass the tools selected for this assistant to the model.

#     Deep agent built-in tools (write_todos, filesystem, etc.) are always kept.
#     Custom tools are filtered to only those in selected_tools.
#     """
#     ctx = request.runtime.context or Context()
#     selected = set(ctx.selected_tools)

#     filtered = [
#         t for t in request.tools
#         if not (hasattr(t, "name") and t.name in CUSTOM_TOOL_NAMES)
#         or (hasattr(t, "name") and t.name in selected)
#     ]

#     return handler(request.override(tools=filtered))

def _memories_namespace(rt):
    """Use assistant_id as the namespace to isolate each assistant's memories."""
    if rt.server_info is not None and rt.server_info.assistant_id:
        return (rt.server_info.assistant_id,)
    return ("default-agent",)


async def make_graph(runtime: Runtime[Context]):

    configurable = runtime.get("configurable", {})
    llm = configurable.get("model", "anthropic:claude-haiku-4-5")
    selected_tools = configurable.get("selected_tools", ["get_todays_date"])
    prompt = configurable.get("system_prompt", "You are a helpful AI assistant.")
    agent_name = configurable.get("name", "react_agent")

    # Route /memories/ to the persistent LangGraph store; everything else stays ephemeral.
    # The namespace factory must return (assistant_id,) to match what was stored via the SDK.
    backend = CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": StoreBackend(namespace=_memories_namespace)},
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