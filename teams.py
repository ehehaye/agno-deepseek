"""Team examples: coordinate (leader synthesizes) and route (direct specialist)."""

from agno.team import Team, TeamMode

from agents import basicAgent, billingAgent, reasonAgent, techAgent
from config import chatModel
from db import db

# coordinate (default): leader delegates work and synthesizes the final answer.
team = Team(
    name="My Team",
    description="A team of agents working together",
    model=chatModel(),
    members=[basicAgent, reasonAgent],
    db=db,
    add_history_to_context=True,
    share_member_interactions=True,
    show_members_responses=True,
    markdown=True,
)

# route: the leader selects one specialist and returns that member's answer.
# Use the TeamMode enum: AgentOS serializes it via `mode.value`.
supportTeam = Team(
    name="Support Team",
    description="Routes each ticket to the right specialist.",
    model=chatModel(),
    mode=TeamMode.route,
    respond_directly=True,
    members=[billingAgent, techAgent],
    db=db,
    markdown=True,
)
