from agno.agent import Agent
from agno.team import Team
from agno.models.deepseek import DeepSeek
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb
from agno.approval import approval
from agno.tools import tool
from agno.os.interfaces.agui import AGUI

@approval
@tool(requires_confirmation=True)
def delete_user_data(user_id: str) -> str:
    """Permanently delete all data for a user. Requires admin approval."""
    return f"All data for user {user_id} has been deleted."

basicAgent = Agent(
    name="basic agent",
    model=DeepSeek(id="deepseek-chat"),
    tools=[delete_user_data],
    markdown=True,
)

reasonAgent = Agent(
    name="reason agent",
    model=DeepSeek(id="deepseek-v4-flash"),
    reasoning=True,          # enable reasoning capabilities
    reasoning_max_steps=5,   # optional: set maximum reasoning steps
    markdown=True,
)

team = Team(
    name="My Team",
    description="A team of agents working together",
    model=DeepSeek(id="deepseek-chat"),
    members=[basicAgent, reasonAgent],
    markdown=True,
)

db = SqliteDb(db_file="data/agentos.db")

agent_os = AgentOS(
    name="My AgentOS",
    agents=[basicAgent, reasonAgent],
    teams=[team],
    interfaces=[AGUI(agent=reasonAgent)],
    workflows=None,
    knowledge=None,
    db=db,
    tracing=False
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)