"""Define the configurable parameters for the agent."""

from typing import Annotated, Literal
from pydantic import BaseModel, Field


class Context(BaseModel):
    """The runtime context for the agent."""

    system_prompt: str = Field(
        default="You are a helpful AI assistant. Your memories are loaded from middleware and are stored in /memories/AGENTS.md. If no /memories/AGENTS.md exists, you can create one to store memories.",
        description="The system prompt to use for the agent's interactions. "
        "This prompt sets the context and behavior for the agent."
    )

    model: Annotated[
            Literal[
                "anthropic:claude-haiku-4-5",
                "anthropic:claude-sonnet-4-5",
                "openai:gpt-5",
                "openai:gpt-5-mini"
            ],
            {"__template_metadata__": {"kind": "llm"}},
        ] = Field(
            default="anthropic:claude-haiku-4-5",
            description="The name of the language model to use for the agent's main interactions. "
        "Should be in the form: provider/model-name."
    )

    selected_tools: list[Literal["finance_research", "advanced_research", "basic_research", "get_todays_date", "langchain_docs"]] = Field(
        default = ["finance_research", "advanced_research", "basic_research", "get_todays_date", "langchain_docs"],
        description="The list of tools to use for the agent's interactions. "
        "This list should contain the names of the tools to use."
    )

    name: str = Field(
        default="react_agent",
        description="The name of the agent."
    )