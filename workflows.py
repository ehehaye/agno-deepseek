"""Workflow (pipeline) examples with Step, Parallel, Condition, Loop, Router, HITL."""

from agno.workflow import (
    Condition,
    HumanReview,
    Loop,
    OnReject,
    Parallel,
    Router,
    Step,
    StepInput,
    StepOutput,
    Workflow,
)

from agents import billingAgent, criticAgent, researcherAgent, techAgent, writerAgent
from db import db


def inputMentionsRisk(step_input: StepInput) -> bool:
    text = str(step_input.input or "").lower()
    return any(word in text for word in ("risk", "security", "compliance", "风险", "安全", "合规"))


def noteNoRisk(step_input: StepInput) -> str:
    return "No risk keywords detected; proceed with the standard review."


def collectText(output: StepOutput) -> list[str]:
    """Flatten StepOutput trees; containers like Condition keep payload in `steps`."""
    content = str(output.content).strip() if output.content else ""
    texts = [content] if content and output.step_type not in ("Condition", "Router") else []
    for child in output.steps or []:
        for text in collectText(child):
            if text not in content:
                texts.append(text)
    return texts


def assembleDraft(step_input: StepInput) -> str:
    """Rebuild the working context after the conditional branch."""
    sections = []
    for name, output in (step_input.previous_step_outputs or {}).items():
        for text in collectText(output):
            sections.append(f"### {name}\n{text}")
    return "\n\n".join(sections) or str(step_input.input or "")


def refinementComplete(outputs: list[StepOutput]) -> bool:
    if not outputs:
        return False
    return "READY TO PUBLISH" in str(outputs[-1].content).upper()


def publishReport(step_input: StepInput) -> str:
    outputs = list((step_input.previous_step_outputs or {}).values())
    # Loop/Router containers put the real payload in `steps`; take the last one.
    texts = collectText(outputs[-1]) if outputs else []
    report = texts[-1] if texts else str(step_input.previous_step_content or step_input.input or "")
    return f"PUBLISHED\n\n{report}"


researchPipeline = Workflow(
    name="Research Pipeline",
    description="Research -> draft/review in parallel -> risk gate -> refine -> approved publish.",
    db=db,
    add_workflow_history_to_steps=True,
    steps=[
        Step(
            name="research",
            description="Build the research outline.",
            agent=researcherAgent,
        ),
        # Run independent branches concurrently.
        Parallel(
            Step(name="draft", description="Write the first draft.", agent=writerAgent),
            Step(name="risk-review", description="Find risks and gaps.", agent=criticAgent),
            name="draft-and-review",
        ),
        # Conditional branch: extra mitigation work only for risky topics.
        Condition(
            name="risk-gate",
            evaluator=inputMentionsRisk,
            steps=[Step(name="mitigation-plan", agent=criticAgent)],
            else_steps=[Step(name="no-risk-note", executor=noteNoRisk)],
        ),
        # Condition only returns a status line; rebuild the full working context
        # (research + parallel draft/review + branch output) for the revision loop.
        Step(name="assemble", executor=assembleDraft),
        # Bounded loop: revise at most twice, stop early on 'READY TO PUBLISH'.
        Loop(
            name="refine",
            steps=[Step(name="revise", agent=writerAgent)],
            max_iterations=2,
            end_condition=refinementComplete,
            forward_iteration_output=True,
        ),
        # Step-level HITL: the workflow pauses before publishing until approved.
        # Resume via POST /workflows/{workflow_id}/runs/{run_id}/continue.
        Step(
            name="publish",
            description="Publish the approved report.",
            executor=publishReport,
            human_review=HumanReview(
                requires_confirmation=True,
                confirmation_message="Publish the final report?",
                on_reject=OnReject.cancel,
            ),
        ),
    ],
)


def routeTicket(step_input: StepInput) -> str:
    text = str(step_input.input or "").lower()
    if any(word in text for word in ("invoice", "refund", "billing", "账单", "退款")):
        return "billing"
    return "technical"


# Router: pick exactly one specialist branch based on the ticket content.
supportRouterWorkflow = Workflow(
    name="Support Router",
    description="Route a support ticket to billing or technical.",
    db=db,
    steps=[
        Router(
            name="ticket-router",
            choices=[
                Step(name="billing", agent=billingAgent),
                Step(name="technical", agent=techAgent),
            ],
            selector=routeTicket,
        )
    ],
)
