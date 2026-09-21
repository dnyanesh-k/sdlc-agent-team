"""Agent definitions for round-robin coordination."""

from __future__ import annotations

from agents import Agent, RunContextWrapper, function_tool

from models import GroupChatContext

@function_tool
def get_conversation_summary(context: RunContextWrapper[GroupChatContext]) -> str:
    """Get summary of conversation so far."""
    return context.context.summary()

def _pm_instructions(context: RunContextWrapper[GroupChatContext]):
    return f"""You are the Product Manager. Your job:
1. Turn the feature request into clear, testable requirements.
2. Review the developer's work and verify it meets requirements.
3. When ALL unit tests pass and requirements are met, end your response with
   the word TERMINATE on its own line.

Feature request: {context.context.feature_requests}
Phase: {context.context.current_phase.value}
Turn: {context.context.turn_count}/{context.context.max_turns}

{context.context.summary()}

If this is the first turn, define requirements clearly.
If the developer just reported tests, decide: TERMINATE if all pass, or request fixes.
Be concise."""


product_manager = Agent(
    name="ProductManager",
    instructions=_pm_instructions,
    tools=[get_conversation_summary],
    model="qwen3.5:0.8b"
)

def _developer_instructions(ctx: RunContextWrapper[GroupChatContext], agent: Agent) -> str:
    return f"""You are the Developer. Your job:
1. Implement code based on the Product Manager's requirements.
2. Write complete, runnable Python code.
3. Write comprehensive unit tests using Python's unittest module.
4. Report test results clearly with pass/fail counts.

Feature request: {ctx.context.feature_request}
Phase: {ctx.context.current_phase.value}

{ctx.context.summary()}

Write complete, runnable Python code. No placeholders or TODOs.
Follow PEP 8. Include error handling.
Write self-contained tests covering happy path, edge cases, and errors."""

developer = Agent(
    name="DeveloperAgent",
    instructions=_developer_instructions,
    tools=[get_conversation_summary],
    model="qwen3.5:0.8b"
)