# agno-deepseek

Demo project wiring the [Agno](https://docs.agno.com) agent framework to the DeepSeek API, served as an AgentOS app.

## Project

- Python >= 3.14 (`.python-version` = `3.14`), dependencies managed with **uv**.
- Flat top-level modules (not a package): `config.py`, `db.py`, `tools.py`, `agents.py`, `teams.py`, `workflows.py`, `main.py`.
- `src/hitl/` is an empty placeholder directory; `scripts/init.sh` recreates the venv from scratch.

## Commands

```bash
uv sync                       # install deps into .venv
uv run main.py                # run the app (agent_os.serve, reload=True)
source .venv/bin/activate     # optional, for a plain python shell
sh scripts/init.sh            # nuke .venv + __pycache__ and reinstall
```

No test suite, linter, or formatter is configured — do not invent test/lint commands.

## Architecture

One-way import direction: `config` / `db` / `tools` → `agents` → `teams` / `workflows` → `main`.

- `config.py` — `chatModel()` returns a fresh `DeepSeek(id="deepseek-chat")` per agent.
- `db.py` — shared `db = SqliteDb(db_file="data/agentos.db")` (gitignored via `data/*`).
- `tools.py` — `calculator`, read-only `runbookReader` (`FileTools(base_dir="data")`), plus three HITL tools: `delete_user_data` (confirmation + `@approval`), `escalate_to_human` (`requires_user_input`), `deploy_release` (`external_execution`).
- `agents.py` — standalone agents (`basicAgent`, `memoryAgent` with `MemoryManager`, `reasonAgent`, `structuredAgent` with `output_schema=ActionPlan`), pipeline agents (`researcherAgent`, `writerAgent`, `criticAgent`), and routing specialists (`billingAgent`, `techAgent`).
- `teams.py` — `team` (coordinate, basic + reason agents, used by `AGUI`) and `supportTeam` (`TeamMode.route`, billing/technical specialists).
- `workflows.py` — `researchPipeline` (`Step`, `Parallel`, `Condition`, `Loop`, step-level `HumanReview`, custom executor steps) and `supportRouterWorkflow` (`Router`).
- `main.py` — `AgentOS(agents=..., teams=..., workflows=..., interfaces=[...], db=db)`, `app = agent_os.get_app()`, server entry point.
- `AGUI` interfaces are mounted at `/endpoint/reason`, `/endpoint/basic`, and `/endpoint/team`.

Implementation notes:
- Team `mode` must be a `TeamMode` enum (e.g. `TeamMode.route`): AgentOS serializes it via `mode.value`, so a plain string breaks `GET /teams`.
- Container steps (`Condition`, `Loop`, `Router`) put only a status line in `.content`; real payload lives in `.steps`. `assembleDraft` and `publishReport` flatten that tree.
- AgentOS routes have no `/agno` prefix: use `/agents`, `/teams`, `/workflows`, `/sessions`, `/approvals`.

## Conventions

- Add capabilities as Agno objects built from `agno.models.deepseek.DeepSeek`; place new objects in the matching module and register agents/teams/workflows in the `AgentOS(...)` lists in `main.py` (`knowledge=None` unless used).
- Keep imports one-way (see above) to avoid cycles.
- Instance names are camelCase (`basicAgent`, `researchPipeline`, `agent_os`) — match that style when adding objects.
- Commit messages are emoji-prefixed and imperative: `✨ add ...`, `➕ add ...`, `🎉 Init`.
- Never commit `.venv/`, `__pycache__/`, or `data/*` (already in `.gitignore`).

## Notes

- Requires `DEEPSEEK_API_KEY` in the environment (no `.env` is checked in).
