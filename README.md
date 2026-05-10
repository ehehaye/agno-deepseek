# Agno DeepSeek

A demo integrating [Agno](https://docs.agno.com) framework with [DeepSeek API](https://api-docs.deepseek.com).

## Prerequisites

- **Python 3.8+** (recommended 3.11+)
- **Homebrew** (for macOS users)
- **uv** - An extremely fast Python package installer and resolver
- **DeepSeek API Key** - Set your `DEEPSEEK_API_KEY` environment variable

### Installation of Prerequisites

```bash
brew install uv
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
uv sync
```

This command will install all required packages specified in `pyproject.toml`.

## Running the Application

Execute the demo application with:

```bash
uv run main.py
```
