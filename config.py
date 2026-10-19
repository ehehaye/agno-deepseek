"""Shared model factory and database instance."""

from agno.db.sqlite import SqliteDb
from agno.models.deepseek import DeepSeek


def chatModel() -> DeepSeek:
    """Return a fresh DeepSeek chat model for each agent."""
    return DeepSeek(id="deepseek-chat")


# Every agent, team, and workflow shares one SQLite database.
db = SqliteDb(db_file="data/agentos.db")
