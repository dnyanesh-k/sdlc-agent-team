"""Agent definitions for round-robin coordination."""

from __future__ import annotations

from agents import Agent, RunContextWrapper, function_tool, set_tracing_disabled, set_default_openai_client
from openai import AsyncOpenAI

from models import GroupChatContext
from tools import save_code_file

BASE_URL = "http://localhost:11434/v1"


@function_tool
def get_conversation_summary(context: RunContextWrapper[GroupChatContext]) -> str:
    """Get summary of conversation so far."""
    return context.context.summary()


def _pm_instructions(context: RunContextWrapper[GroupChatContext], agent: Agent):
    has_code = bool(context.context.code.files)
    return f"""You are the Product Manager. Your job:
1. Turn the feature request into clear, testable requirements.
2. Review the developer's work and verify it meets requirements.
3. When ALL unit tests pass and requirements are met, end your response with
   the word TERMINATE on its own line.

Feature request: {context.context.feature_requests}
Phase: {context.context.current_phase.value}
Turn: {context.context.turn_count}/{context.context.max_turns}
Has Developer Written Code?: {has_code}

{context.context.summary()}

If this is the first turn, define requirements clearly.
If the developer just reported tests, decide: TERMINATE if all pass, or request fixes.
Be concise."""


ollama_client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key="ollama"
)

set_tracing_disabled(True)

set_default_openai_client(ollama_client)


product_manager = Agent(
    name="ProductManager",
    instructions=_pm_instructions,
    # tools=[get_conversation_summary],
    model="llama3.2:1b"
)


def _developer_instructions(ctx: RunContextWrapper[GroupChatContext], agent: Agent) -> str:
    return f"""You are the Developer. Your job:
1. Implement code based on the Product Manager's requirements.
2. Use the 'save_code_file' tool to write your python implementation and test files into the workspace.
3. Write complete, runnable Python code without placeholders.
4. Once you have successfully saved all files using the tool, summarize your work for the Product Manager.

Feature request: {ctx.context.feature_requests}
Phase: {ctx.context.current_phase.value}

{ctx.context.summary()}

Write complete, runnable Python code. No placeholders or TODOs.
Follow PEP 8. Include error handling.
Write self-contained tests covering happy path, edge cases, and errors."""


developer = Agent(
    name="DeveloperAgent",
    instructions=_developer_instructions,
    tools=[save_code_file],
    model="qwen3.5:0.8b"
)