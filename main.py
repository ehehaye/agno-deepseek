from agno.agent import Agent
from agno.team import Team
from agno.models.deepseek import DeepSeek
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb

basicAgent = Agent(
    name="basic agent",
    model=DeepSeek(id="deepseek-chat"),
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
    members=[reasonAgent, basicAgent],
    markdown=True,
)

db = SqliteDb(db_file="data/agentos.db")

agent_os = AgentOS(
    name="My AgentOS",
    agents=[reasonAgent, basicAgent],
    teams=[team],
    workflows=None,
    knowledge=None,
    db=db,
    tracing=False
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)