from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.os import AgentOS

agent = Agent(model=DeepSeek(id="deepseek-chat"), markdown=True)

agent_os = AgentOS(
    name="My AgentOS",
    agents=[agent],
    teams=None,
    workflows=None,
    knowledge=None,
    db=None,
    tracing=False
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)