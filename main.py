from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb

agent = Agent(
    model=DeepSeek(id="deepseek-chat"),
    reasoning=True,          # enable reasoning capabilities
    reasoning_max_steps=5,   # optional: set maximum reasoning steps
    markdown=True,
)

db = SqliteDb(db_file="data/agentos.db")

agent_os = AgentOS(
    name="My AgentOS",
    agents=[agent],
    teams=None,
    workflows=None,
    knowledge=None,
    db=db,
    tracing=False
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)