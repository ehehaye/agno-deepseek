"""AgentOS entry point: register agents, teams, and workflows, then serve the app.

Module layout:
  config.py     shared DeepSeek model factory
  db.py         shared SqliteDb
  tools.py      built-in tools + three HITL tool modes
  agents.py     standalone agents and the specialists used by teams/workflows
  teams.py      coordinate and route team examples
  workflows.py  pipeline and router workflow examples
"""

from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

from agents import basicAgent, memoryAgent, reasonAgent, structuredAgent
from db import db
from teams import supportTeam, team
from workflows import researchPipeline, supportRouterWorkflow

agent_os = AgentOS(
    name="My AgentOS",
    agents=[basicAgent, memoryAgent, reasonAgent, structuredAgent],
    teams=[team, supportTeam],
    workflows=[researchPipeline, supportRouterWorkflow],
    interfaces=[
        AGUI(agent=reasonAgent, prefix="/endpoint/reason"),
        AGUI(agent=basicAgent, prefix="/endpoint/basic"),
        AGUI(team=team, prefix="/endpoint/team"),
    ],
    knowledge=None,
    db=db,
    tracing=False,
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)
