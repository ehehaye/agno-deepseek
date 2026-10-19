"""Agent examples: tools/HITL, memory, reasoning, and structured output."""

from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.memory import MemoryManager
from agno.models.deepseek import DeepSeek

from config import chatModel
from db import db
from tools import (
    calculator,
    delete_user_data,
    deploy_release,
    escalate_to_human,
    runbookReader,
)


# ---------------------------------------------------------------------------
# Standalone agents (registered directly on AgentOS)
# ---------------------------------------------------------------------------
basicAgent = Agent(
    name="basic agent",
    model=chatModel(),
    description="General-purpose assistant with tools and human approval gates.",
    instructions=[
        "Use the calculator for arithmetic instead of guessing.",
        "Use the runbook reader when the question refers to local files.",
        "Only call delete_user_data when the user explicitly asks to delete data.",
        "Never claim an approval-gated action succeeded before it is approved.",
    ],
    tools=[calculator, runbookReader, delete_user_data, escalate_to_human, deploy_release],
    db=db,
    update_memory_on_run=True,
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
    markdown=True,
)

# Long-term memory: one model call extracts facts, later runs get them in context.
memoryAgent = Agent(
    name="memory agent",
    model=chatModel(),
    description="Assistant that remembers user preferences across sessions.",
    instructions=["Be concise and apply remembered preferences automatically."],
    db=db,
    memory_manager=MemoryManager(model=chatModel(), db=db),
    update_memory_on_run=True,
    add_memories_to_context=True,
    add_history_to_context=True,
    markdown=True,
)

# Reasoning: a separate reasoning model performs COT before answering.
reasonAgent = Agent(
    name="reason agent",
    model=DeepSeek(id="deepseek-v4-flash"),
    reasoning=True,
    reasoning_model=DeepSeek(id="deepseek-v4-flash"),  # manual COT by default
    reasoning_max_steps=5,
    db=db,
    update_memory_on_run=True,
    add_history_to_context=True,
    markdown=True,
)


class ActionPlan(BaseModel):
    summary: str = Field(description="One-paragraph summary")
    steps: list[str] = Field(description="Ordered, concrete action items")
    owner: str = Field(description="Person or team responsible")


# Structured output: the response is parsed into a Pydantic model.
structuredAgent = Agent(
    name="structured agent",
    model=chatModel(),
    description="Turns a request into a structured action plan.",
    instructions=["Return a plan that can be executed as written."],
    output_schema=ActionPlan,
    db=db,
)


# ---------------------------------------------------------------------------
# Pipeline agents (used by workflows.py)
# ---------------------------------------------------------------------------
researcherAgent = Agent(
    name="researcher agent",
    model=chatModel(),
    role="Research the topic and produce an outline with facts and open questions.",
    instructions=["Be factual; list assumptions and unknowns explicitly."],
)

writerAgent = Agent(
    name="writer agent",
    model=chatModel(),
    role="Write and revise a clear, well-structured report.",
    instructions=[
        "Use markdown headings and short paragraphs.",
        "Finish with the exact line 'READY TO PUBLISH' when no further revision is needed.",
    ],
)

criticAgent = Agent(
    name="critic agent",
    model=chatModel(),
    role="Review the draft for risks, gaps, and unstated assumptions.",
    instructions=["Return a prioritized list of risks and concrete fixes."],
)


# ---------------------------------------------------------------------------
# Routing specialists (used by supportTeam and the Support Router workflow)
# ---------------------------------------------------------------------------
billingAgent = Agent(
    name="billing agent",
    model=chatModel(),
    description="Handles invoices, refunds, and billing questions.",
    instructions=["Answer billing questions only; hand off anything else."],
)

techAgent = Agent(
    name="technical agent",
    model=chatModel(),
    description="Handles API, configuration, and debugging questions.",
    instructions=["Give concrete reproduction steps and fixes."],
)
