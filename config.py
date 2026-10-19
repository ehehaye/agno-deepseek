"""Shared model factory."""

from agno.models.deepseek import DeepSeek


def chatModel() -> DeepSeek:
    """Return a fresh DeepSeek chat model for each agent."""
    return DeepSeek(id="deepseek-chat")
