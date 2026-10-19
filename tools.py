"""Tool examples: built-in toolkits plus the three HITL tool modes."""

from pathlib import Path
from typing import Optional

from agno.approval import approval
from agno.tools import tool
from agno.tools.calculator import CalculatorTools
from agno.tools.file import FileTools

calculator = CalculatorTools()

# Read-only access to data/ so the model cannot modify or delete local files.
runbookReader = FileTools(
    base_dir=Path("data"),
    enable_save_file=False,
    enable_delete_file=False,
    enable_replace_file_chunk=False,
)


# HITL #1: blocking approval. The run pauses until a human approves the call.
@approval
@tool(requires_confirmation=True)
def delete_user_data(user_id: str) -> str:
    """Permanently delete all data for a user. Requires admin approval."""
    return f"All data for user {user_id} has been deleted."


# HITL #2: user input. The model supplies `reason`, the operator fills `ticket_id`.
@tool(requires_user_input=True, user_input_fields=["ticket_id"])
def escalate_to_human(reason: str, ticket_id: Optional[str] = None) -> str:
    """Escalate an issue to a human operator and attach it to a ticket."""
    return f"Escalated to human operator under ticket {ticket_id}. Reason: {reason}"


# HITL #3: external execution. The caller runs the tool outside the agent process.
@tool(external_execution=True)
def deploy_release(version: str) -> str:
    """Deploy a release. Executed by an external operator, not by the agent."""
    return f"Release {version} deployed."
