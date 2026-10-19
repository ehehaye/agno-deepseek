# agno-deepseek

[English](#english) · [中文](#chinese)

> A demo project that wires the [Agno](https://docs.agno.com) agent framework to the
> [DeepSeek API](https://api-docs.deepseek.com) and serves everything as an **AgentOS** app.
>
> 一个把 [Agno](https://docs.agno.com) 智能体框架接到 [DeepSeek API](https://api-docs.deepseek.com)，
> 并以 **AgentOS** 形式提供服务的示例项目。

---

<a id="english"></a>

## English

### 1. Overview

`agno-deepseek` is a compact but complete playground for the main Agno building blocks:

- **Agents** — plain agents, long-term memory, reasoning models, and structured (Pydantic) output.
- **Teams** — `coordinate` (leader synthesizes) and `route` (leader picks a specialist).
- **Workflows** — sequential steps, parallel branches, conditional branches, bounded loops,
  a content router, and step-level human review.
- **Tools & HITL** — built-in toolkits plus all three human-in-the-loop modes:
  confirmation/approval, user input, and external execution.
- **Serving** — an `AgentOS` FastAPI app with REST routes, SSE streaming, an OpenAPI
  docs page, and AG-UI protocol endpoints.

All model calls go through `DeepSeek`; all state (sessions, runs, memories, approvals)
is persisted in a local SQLite database.

### 2. Feature highlights

| Capability | Where |
| --- | --- |
| Tool-calling agent with calculator + read-only file access | `agents.basicAgent` |
| Three HITL modes | `tools.py` + `agents.basicAgent` |
| Long-term user memory | `agents.memoryAgent` (`MemoryManager`) |
| Chain-of-thought reasoning | `agents.reasonAgent` (`reasoning=True`) |
| Typed structured output | `agents.structuredAgent` (`output_schema=ActionPlan`) |
| Multi-agent coordination | `teams.team` (`TeamMode.coordinate`) |
| Specialist routing team | `teams.supportTeam` (`TeamMode.route`) |
| Research/draft/review/refine/publish pipeline | `workflows.researchPipeline` |
| Ticket routing workflow | `workflows.supportRouterWorkflow` (`Router`) |
| Concurrent workflow branches | `Parallel` step |
| Conditional workflow branch | `Condition` step (risk keywords, incl. Chinese) |
| Bounded revision loop | `Loop` step (`max_iterations=2`, early stop) |
| Workflow-level human approval | `HumanReview` on the `publish` step |
| REST + SSE + OpenAPI | `AgentOS` (`main.py`) |
| AG-UI endpoints | `/endpoint/reason`, `/endpoint/basic`, `/endpoint/team` |
| Persistent sessions / history / memory / approvals | `data/agentos.db` (SQLite) |

### 3. Tech stack

| Component | Version / choice |
| --- | --- |
| Python | `>= 3.14` (pinned by `.python-version`) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Agent framework | `agno >= 2.6.5` |
| Model provider | DeepSeek (`agno.models.deepseek.DeepSeek`) |
| Web layer | FastAPI + Uvicorn (provided by AgentOS) |
| Persistence | SQLAlchemy + aiosqlite (`SqliteDb`) |
| Agent UI protocol | `ag-ui-protocol >= 0.1.19` |
| Extras | `websockets` (AgentOS debugging), `socksio` |

### 4. Requirements

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed
- A **DeepSeek API key** available as `DEEPSEEK_API_KEY` in the process environment

Install `uv` on macOS with Homebrew if needed:

```bash
brew install uv
```

### 5. Quick start

```bash
git clone https://github.com/ehehaye/agno-deepseek.git
cd agno-deepseek
uv sync
export DEEPSEEK_API_KEY="sk-..."
mkdir -p data
uv run main.py
```

The server starts on **http://localhost:7777** by default.

Useful URLs:

| URL | Purpose |
| --- | --- |
| `http://localhost:7777/` | AgentOS home |
| `http://localhost:7777/docs` | Swagger UI / OpenAPI |
| `http://localhost:7777/redoc` | ReDoc |
| `http://localhost:7777/openapi.json` | Raw OpenAPI schema |

Optional: connect [os.agno.com](https://os.agno.com) to the local endpoint to browse and
chat with the agents, teams, and workflows in a web UI.

### 6. Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | Yes | DeepSeek API credential used by every model call. |

Notes:

- The app does not commit any `.env`; `.env` / `.env.*` are gitignored. Export the key in
  your shell (or use your shell profile / `direnv`).
- Model IDs are hard-coded:
  - `deepseek-chat` — `config.chatModel()` plus the specialist/pipeline agents.
  - `deepseek-v4-flash` — model and reasoning model of `reasonAgent`.
  If your DeepSeek account does not expose one of these IDs, change it in
  [`config.py`](config.py) / [`agents.py`](agents.py).
- No authentication is configured by default. For a Bearer-token setup, set
  `OS_SECURITY_KEY` (read by Agno's `AgnoAPISettings`) before starting the server.

### 7. Project structure

```text
agno-deepseek/
├── main.py            # AgentOS entry point: registers agents/teams/workflows/interfaces
├── config.py          # chatModel(): fresh DeepSeek("deepseek-chat") per agent
├── db.py              # shared SqliteDb("data/agentos.db")
├── tools.py           # calculator, runbookReader, and the 3 HITL tools
├── agents.py          # standalone agents + pipeline agents + routing specialists
├── teams.py           # coordinate team + route team
├── workflows.py       # research pipeline + support router workflow
├── pyproject.toml     # dependencies (managed by uv)
├── uv.lock            # locked dependency graph
├── .python-version    # 3.14
├── scripts/
│   └── init.sh        # remove .venv/__pycache__, recreate venv, uv sync
├── src/
│   └── hitl/          # empty placeholder package directory
└── data/              # runtime state, gitignored (agentos.db, runbook files)
```

`data/` is created automatically when `SqliteDb` initializes, but creating it up front is
harmless and makes the first run more predictable.

### 8. Architecture

One-way imports — no cycles:

```text
config.py ─┐
db.py ─────┼──> agents.py ──> teams.py ──────┐
tools.py ──┘                └─> workflows.py ─┼──> main.py
                                                │
                              agno.os.AgentOS <─┘
```

- `config.py` returns a **fresh** model instance per agent, so each agent owns its own
  client state.
- `db.py` exposes a single shared `SqliteDb`, used by every agent, team, and workflow.
- `agents.py` defines both the agents registered directly on AgentOS and the internal
  specialists consumed by teams/workflows.
- `teams.py` and `workflows.py` import agents but never the reverse.
- `main.py` is the only module that constructs `AgentOS` and starts the server.

### 9. Registered components

IDs are derived automatically from names via
`agno.utils.string.generate_id_from_name(name)`:
lowercase, spaces and underscores replaced with `-`.

#### 9.1 Agents

| Variable | Agent ID | Model | Registered on AgentOS | Highlights |
| --- | --- | --- | --- | --- |
| `basicAgent` | `basic-agent` | `deepseek-chat` | Yes | Calculator + read-only `FileTools` + all 3 HITL tools; memory updates, history (5 runs), datetime, markdown |
| `memoryAgent` | `memory-agent` | `deepseek-chat` | Yes | `MemoryManager` extracts facts; memories injected into later runs |
| `reasonAgent` | `reason-agent` | `deepseek-v4-flash` | Yes | Manual CoT with `reasoning=True`, `reasoning_max_steps=5` |
| `structuredAgent` | `structured-agent` | `deepseek-chat` | Yes | `output_schema=ActionPlan` (`summary`, `steps`, `owner`) |
| `researcherAgent` | `researcher-agent` | `deepseek-chat` | No | Produces fact-based outline for the pipeline |
| `writerAgent` | `writer-agent` | `deepseek-chat` | No | Drafts/revises markdown; emits `READY TO PUBLISH` |
| `criticAgent` | `critic-agent` | `deepseek-chat` | No | Reviews risks/gaps; also writes mitigation plans |
| `billingAgent` | `billing-agent` | `deepseek-chat` | No | Billing specialist for the route team/workflow |
| `techAgent` | `technical-agent` | `deepseek-chat` | No | Technical specialist for the route team/workflow |

#### 9.2 Teams

| Variable | Team ID | Mode | Members | Behavior |
| --- | --- | --- | --- | --- |
| `team` | `my-team` | `coordinate` (default) | `basicAgent`, `reasonAgent` | Leader delegates, shares member interactions, synthesizes the final answer |
| `supportTeam` | `support-team` | `TeamMode.route` | `billingAgent`, `techAgent` | Leader selects exactly one specialist and returns that answer directly |

`TeamMode.route` is imported from `agno.team`; using the enum (not the string `"route"`)
is required because AgentOS serializes it with `mode.value`.

#### 9.3 Workflows

| Variable | Workflow ID | Composition |
| --- | --- | --- |
| `researchPipeline` | `research-pipeline` | `Step` → `Parallel` → `Condition` → executor step → `Loop` → `Step` with `HumanReview` |
| `supportRouterWorkflow` | `support-router` | Single `Router` selecting a `billing` or `technical` step |

Research pipeline:

```text
research (researcherAgent)
   │
   ├── draft        (writerAgent)   ─┐  Parallel
   └── risk-review  (criticAgent)   ─┘
   │
risk-gate (Condition: inputMentionsRisk)
   ├── risky  → mitigation-plan (criticAgent)
   └── normal → no-risk-note    (executor)
   │
assemble (executor: assembleDraft — rebuilds full context)
   │
refine (Loop, max_iterations=2, stop when "READY TO PUBLISH")
   │
publish (executor: publishReport + HumanReview, OnReject.cancel)
   │
PUBLISHED ...
```

Risk keywords are `risk`, `security`, `compliance`, `风险`, `安全`, `合规`
(case-insensitive).

Support router:

```text
ticket
  │
ticket-router (selector: routeTicket)
  ├── contains invoice/refund/billing/账单/退款 → billingAgent
  └── otherwise                                  → techAgent
```

### 10. Tools and human-in-the-loop

[`tools.py`](tools.py) defines:

| Tool | Kind | Behavior |
| --- | --- | --- |
| `calculator` | `CalculatorTools()` | Arithmetic without model guessing |
| `runbookReader` | `FileTools(base_dir="data")` | Read/search under `data/`; save, delete, and chunk-replace disabled |
| `delete_user_data` | `@approval` + `requires_confirmation=True` | Pauses the run; an admin must resolve the approval |
| `escalate_to_human` | `requires_user_input=True`, field `ticket_id` | Pauses the run; the operator supplies `ticket_id` |
| `deploy_release` | `external_execution=True` | Pauses the run; the caller executes the deployment outside the agent and returns the result |

How the pause/resume cycle works:

1. The agent run stops mid-tool and returns a run whose status is **paused**.
2. You inspect the pending requirement (tool name, arguments, approval ID, user-input
   schema) in the run output.
3. You satisfy it through one of the paths below.
4. Call the `continue` endpoint with the same `run_id` and `session_id`; the agent resumes
   from the paused tool call.

| HITL mode | How to resolve | Resume payload |
| --- | --- | --- |
| Admin approval (`delete_user_data`) | `POST /approvals/{approval_id}/resolve` with `{"status": "approved"}` | `/continue` with `session_id` only (`tools` may be empty) |
| User input (`escalate_to_human`) | Provide the field value | `/continue` with `tools` JSON containing `user_input_schema` values and `answered: true` |
| External execution (`deploy_release`) | Execute the action yourself | `/continue` with `tools` JSON containing the tool's `result` |

For workflow-level HITL, [`workflows.py`](workflows.py) attaches `HumanReview` to the
`publish` step. The workflow pauses before publishing and resumes through
`POST /workflows/research-pipeline/runs/{run_id}/continue`.

### 11. Memory, history, and persistence

- Every registered agent, team, and workflow shares `db = SqliteDb("data/agentos.db")`.
- The database stores sessions, runs, messages, user memories, and approvals.
- `data/*` is gitignored: delete `data/agentos.db` to reset all state.
- History/context settings:
  - `basicAgent`: `add_history_to_context=True`, `num_history_runs=5`, `add_datetime_to_context=True`.
  - `memoryAgent`: `memory_manager=MemoryManager(...)`, `update_memory_on_run=True`,
    `add_memories_to_context=True`.
  - `reasonAgent`: `update_memory_on_run=True`, `add_history_to_context=True`.
- `runbookReader` resolves `base_dir` relative to the working directory — start the app
  from the repository root so it points at `./data`.

### 12. API

#### 12.1 AgentOS REST routes

No `/agno` prefix.

| Resource | Routes |
| --- | --- |
| Agents | `GET /agents`, `GET /agents/{agent_id}`, `POST /agents/{agent_id}/runs`, `POST /agents/{agent_id}/runs/{run_id}/continue`, `POST /agents/{agent_id}/runs/{run_id}/cancel`, `POST /agents/{agent_id}/runs/{run_id}/resume`, `GET /agents/{agent_id}/runs`, `GET /agents/{agent_id}/runs/{run_id}` |
| Teams | `GET /teams`, `GET /teams/{team_id}`, `POST /teams/{team_id}/runs`, `POST /teams/{team_id}/runs/{run_id}/continue`, `POST /teams/{team_id}/runs/{run_id}/cancel`, `POST /teams/{team_id}/runs/{run_id}/resume`, `GET /teams/{team_id}/runs`, `GET /teams/{team_id}/runs/{run_id}` |
| Workflows | `GET /workflows`, `GET /workflows/{workflow_id}`, `POST /workflows/{workflow_id}/runs`, `POST /workflows/{workflow_id}/runs/{run_id}/continue`, `POST /workflows/{workflow_id}/runs/{run_id}/cancel`, `POST /workflows/{workflow_id}/runs/{run_id}/resume`, `GET /workflows/{workflow_id}/runs`, `GET /workflows/{workflow_id}/runs/{run_id}` |
| Sessions | `GET /sessions`, `POST /sessions`, `GET /sessions/{session_id}`, `GET /sessions/{session_id}/runs`, `GET /sessions/{session_id}/runs/{run_id}`, `POST /sessions/{session_id}/rename`, ... |
| Approvals | `GET /approvals`, `GET /approvals/count`, `GET /approvals/{approval_id}`, `GET /approvals/{approval_id}/status`, `POST /approvals/{approval_id}/resolve`, `DELETE /approvals/{approval_id}` |

**Important:** run requests use `multipart/form-data` (FastAPI `Form` fields), not JSON:

| Field | Default | Meaning |
| --- | --- | --- |
| `message` | required | User input |
| `stream` | `true` | SSE streaming; set `false` for a single JSON response |
| `session_id` | auto | Conversation continuity / resume handle |
| `user_id` | none | Memory and run ownership |
| `background` | `false` | Detach the run and reconnect later with `/resume` |

#### 12.2 AG-UI endpoints

| Prefix | Target |
| --- | --- |
| `/endpoint/basic` | `basicAgent` |
| `/endpoint/reason` | `reasonAgent` |
| `/endpoint/team` | `team` (`my-team`) |

These speak the AG-UI protocol for frontend clients such as CopilotKit.

#### 12.3 Examples

List agents:

```bash
curl -s http://localhost:7777/agents | python -m json.tool
```

Run an agent (non-streaming, easiest to inspect):

```bash
curl -s -X POST http://localhost:7777/agents/basic-agent/runs \
  -F 'message=Use the calculator to compute 1234 * 5678' \
  -F 'stream=false' \
  -F 'user_id=demo' \
  -F 'session_id=demo-session-1'
```

Stream the reasoning agent:

```bash
curl -N -X POST http://localhost:7777/agents/reason-agent/runs \
  -F 'message=Design a rollback plan for a failed database migration.' \
  -F 'stream=true' \
  -F 'user_id=demo'
```

Ask for structured output:

```bash
curl -s -X POST http://localhost:7777/agents/structured-agent/runs \
  -F 'message=Plan the rollout of a new billing provider.' \
  -F 'stream=false'
```

Run the coordinating team:

```bash
curl -s -X POST http://localhost:7777/teams/my-team/runs \
  -F 'message=Summarize 42 * 17 and explain why the result is trustworthy.' \
  -F 'stream=false'
```

Run the routing team:

```bash
curl -s -X POST http://localhost:7777/teams/support-team/runs \
  -F 'message=I was double charged on invoice 8842, please refund one payment.' \
  -F 'stream=false'
```

Run the research pipeline (include a risk keyword to trigger the mitigation branch):

```bash
curl -s -X POST http://localhost:7777/workflows/research-pipeline/runs \
  -F 'message=Write a report on SQLite versus Postgres for this service, including security and compliance risks.' \
  -F 'stream=false' \
  -F 'user_id=demo'
```

Run the support router workflow:

```bash
curl -s -X POST http://localhost:7777/workflows/support-router/runs \
  -F 'message=The API returns 401 after I rotate my key.' \
  -F 'stream=false'
```

Inspect pending approvals:

```bash
curl -s http://localhost:7777/approvals | python -m json.tool
```

Resolve an approval and resume the paused agent run:

```bash
curl -s -X POST http://localhost:7777/approvals/<approval_id>/resolve \
  -H 'Content-Type: application/json' \
  -d '{"status": "approved", "resolved_by": "admin"}'
```

```bash
curl -s -X POST http://localhost:7777/agents/basic-agent/runs/<run_id>/continue \
  -F 'session_id=<session_id>' \
  -F 'stream=false'
```

Provide user input or an external result by passing a `tools` JSON array — the objects
follow `agno.models.response.ToolExecution` (`tool_call_id`, `tool_name`, `tool_args`,
`result`, `user_input_schema`, `answered`, ...):

```bash
curl -s -X POST http://localhost:7777/agents/basic-agent/runs/<run_id>/continue \
  -F 'session_id=<session_id>' \
  -F 'tools=[{"tool_call_id":"<id>","tool_name":"escalate_to_human","user_input_schema":[{"name":"ticket_id","field_type":"str","value":"TCK-123"}]}]' \
  -F 'stream=false'
```

Resume a workflow paused at `publish` by echoing its `step_requirements` back with the
confirmation resolved:

```bash
curl -s -X POST http://localhost:7777/workflows/research-pipeline/runs/<run_id>/continue \
  -F 'session_id=<session_id>' \
  -F 'step_requirements=[{"step_id":"<id>","step_name":"publish","requires_confirmation":true,"confirmed":true}]' \
  -F 'stream=false'
```

> The exact `step_id` and requirement shape come from the paused run response. Copy the
> requirement, set `confirmed: true` (or fill `user_input` / `selected_choices` for other
> modes), and send it back. The web UI or Agno client SDK does this for you.

### 13. Implementation notes

- **Enum for team mode.** `TeamMode.route` must be the enum, not `"route"`; AgentOS
  serializes with `mode.value`.
- **Container payloads.** `Condition`, `Loop`, and `Router` put only a status line in
  `.content`. Real outputs live in `.steps`, which is why `assembleDraft` and
  `publishReport` recursively flatten the tree (`collectText`).
- **Loop termination.** `refinementComplete` checks whether the last output contains
  `READY TO PUBLISH`; otherwise the loop stops at `max_iterations=2`.
- **Publish rejection.** `OnReject.cancel` means rejecting the publish step cancels the
  whole workflow instead of skipping it.
- **Forward iteration output.** `forward_iteration_output=True` lets each revision see the
  previous iteration's output.
- **Read-only file access.** `runbookReader` disables save/delete/chunk-replace and is
  confined to `data/`.
- **Tracing off.** `AgentOS(..., tracing=False)`; set it to `True` if you want trace
  collection in the database.
- **No knowledge base.** `knowledge=None` is passed explicitly.

### 14. Development

```bash
uv sync                       # install/refresh dependencies
uv run main.py                # run with reload=True (development)
source .venv/bin/activate     # optional: plain python shell
sh scripts/init.sh            # delete .venv/__pycache__, recreate venv, uv sync
```

There is **no test suite, linter, or formatter** configured in this repository.

Conventions:

- Flat top-level modules, no package.
- Import direction is one-way: `config` / `db` / `tools` → `agents` → `teams` / `workflows`
  → `main`.
- Instance names are camelCase (`basicAgent`, `researchPipeline`, `agent_os`).
- Commit messages are emoji-prefixed and imperative: `✨ add ...`, `➕ add ...`, `🎉 Init`.
- Never commit `.venv/`, `__pycache__/`, or `data/*`.

### 15. Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `DEEPSEEK_API_KEY` missing / 401 from the model API | Export the key in the same shell that runs `uv run main.py`. |
| Model not found (`deepseek-v4-flash`, etc.) | Your account may not expose that ID; edit `config.py` / `agents.py`. |
| `FileNotFoundError` for `data` files | Run from the repository root and `mkdir -p data`; add runbook files under `data/`. |
| Port 7777 already in use | Stop the other process or pass a different port in `agent_os.serve(...)`. |
| Stale sessions/memories during testing | Delete `data/agentos.db` (destroys all local state). |
| Approval resolve returns `409` | The approval is already resolved/rejected; fetch it first. |
| `/continue` returns `409` | The run is not paused (already running/completed/errored). |
| Python version error | `uv python install 3.14`, or remove `.venv` and run `uv sync` again. |

### 16. Limitations

This is a **demo**, not a production deployment:

- No authentication or authorization is enabled by default.
- The SQLite database is single-file and local.
- Prompts/instructions are intentionally short.
- HITL resolution is exposed directly over HTTP; put it behind real identity and
  authorization before exposing the service.
- Deleting `data/` or the SQLite file permanently removes sessions, memories, and approvals.

---

<a id="chinese"></a>

## 中文文档

### 1. 项目简介

`agno-deepseek` 是一个小巧但完整的 [Agno](https://docs.agno.com) 示例项目，覆盖了框架的主要能力：

- **Agent（智能体）** —— 普通智能体、长期记忆、推理模型、结构化（Pydantic）输出。
- **Team（团队）** —— `coordinate`（协调者汇总答案）与 `route`（协调者选择专家）。
- **Workflow（工作流）** —— 顺序步骤、并行分支、条件分支、有界循环、内容路由以及步骤级人工审核。
- **Tools 与 HITL（Human-in-the-Loop，人在回路）** —— 内置工具集，以及三种人工介入模式：
  确认/审批、用户输入、外部执行。
- **服务化** —— 基于 `AgentOS` 的 FastAPI 应用，提供 REST 路由、SSE 流式响应、
  OpenAPI 文档页以及 AG-UI 协议端点。

所有模型调用都通过 `DeepSeek` 完成；所有状态（会话、运行记录、记忆、审批）
都持久化在本地 SQLite 数据库中。

### 2. 功能一览

| 能力 | 所在位置 |
| --- | --- |
| 带计算器与只读文件访问的工具型智能体 | `agents.basicAgent` |
| 三种 HITL 模式 | `tools.py` + `agents.basicAgent` |
| 长期用户记忆 | `agents.memoryAgent`（`MemoryManager`） |
| 思维链推理 | `agents.reasonAgent`（`reasoning=True`） |
| 强类型结构化输出 | `agents.structuredAgent`（`output_schema=ActionPlan`） |
| 多智能体协作 | `teams.team`（`TeamMode.coordinate`） |
| 专家路由团队 | `teams.supportTeam`（`TeamMode.route`） |
| 研究/起草/评审/修订/发布流水线 | `workflows.researchPipeline` |
| 工单路由工作流 | `workflows.supportRouterWorkflow`（`Router`） |
| 并行工作流分支 | `Parallel` 步骤 |
| 条件工作流分支 | `Condition` 步骤（支持中文风险关键词） |
| 有界修订循环 | `Loop` 步骤（`max_iterations=2`，可提前结束） |
| 工作流级人工审批 | `publish` 步骤上的 `HumanReview` |
| REST + SSE + OpenAPI | `AgentOS`（`main.py`） |
| AG-UI 端点 | `/endpoint/reason`、`/endpoint/basic`、`/endpoint/team` |
| 会话 / 历史 / 记忆 / 审批持久化 | `data/agentos.db`（SQLite） |

### 3. 技术栈

| 组件 | 版本 / 选型 |
| --- | --- |
| Python | `>= 3.14`（由 `.python-version` 固定） |
| 包管理 | [uv](https://docs.astral.sh/uv/) |
| 智能体框架 | `agno >= 2.6.5` |
| 模型提供方 | DeepSeek（`agno.models.deepseek.DeepSeek`） |
| Web 层 | FastAPI + Uvicorn（由 AgentOS 提供） |
| 持久化 | SQLAlchemy + aiosqlite（`SqliteDb`） |
| Agent UI 协议 | `ag-ui-protocol >= 0.1.19` |
| 其他 | `websockets`（AgentOS 调试）、`socksio` |

### 4. 环境要求

- Python **3.14+**
- 已安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)
- 进程环境中存在 **DeepSeek API Key**：`DEEPSEEK_API_KEY`

macOS 上如未安装 `uv`，可使用 Homebrew：

```bash
brew install uv
```

### 5. 快速开始

```bash
git clone https://github.com/ehehaye/agno-deepseek.git
cd agno-deepseek
uv sync
export DEEPSEEK_API_KEY="sk-..."
mkdir -p data
uv run main.py
```

服务默认监听 **http://localhost:7777**。

常用地址：

| 地址 | 用途 |
| --- | --- |
| `http://localhost:7777/` | AgentOS 首页 |
| `http://localhost:7777/docs` | Swagger UI / OpenAPI |
| `http://localhost:7777/redoc` | ReDoc |
| `http://localhost:7777/openapi.json` | 原始 OpenAPI 描述 |

可选：在 [os.agno.com](https://os.agno.com) 连接本地端点，通过 Web UI 浏览并对话
各个 Agent、Team 和 Workflow。

### 6. 配置

| 变量 | 是否必需 | 说明 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 是 | 所有模型调用使用的 DeepSeek 凭据。 |

说明：

- 仓库不提交任何 `.env`；`.env` / `.env.*` 已被 gitignore。请在 shell 中导出该变量
  （也可写入 shell 配置或使用 `direnv`）。
- 模型 ID 是硬编码的：
  - `deepseek-chat` —— `config.chatModel()` 以及专家/流水线智能体。
  - `deepseek-v4-flash` —— `reasonAgent` 的模型与推理模型。
  如果你的 DeepSeek 账号不支持上述某个 ID，请在
  [`config.py`](config.py) / [`agents.py`](agents.py) 中修改。
- 默认未启用鉴权。如需 Bearer Token 鉴权，可在启动前设置 `OS_SECURITY_KEY`
  （由 Agno 的 `AgnoAPISettings` 读取）。

### 7. 项目结构

```text
agno-deepseek/
├── main.py            # AgentOS 入口：注册 agents/teams/workflows/interfaces
├── config.py          # chatModel()：为每个智能体新建 DeepSeek("deepseek-chat")
├── db.py              # 共享 SqliteDb("data/agentos.db")
├── tools.py           # 计算器、只读文件工具、3 个 HITL 工具
├── agents.py          # 独立智能体 + 流水线智能体 + 路由专家
├── teams.py           # coordinate 团队 + route 团队
├── workflows.py       # 研究流水线 + 支持路由工作流
├── pyproject.toml     # 依赖声明（由 uv 管理）
├── uv.lock            # 锁定的依赖图
├── .python-version    # 3.14
├── scripts/
│   └── init.sh        # 删除 .venv/__pycache__，重建虚拟环境并 uv sync
├── src/
│   └── hitl/          # 空的占位目录
└── data/              # 运行时状态，已 gitignore（agentos.db、runbook 文件）
```

`SqliteDb` 初始化时会自动创建 `data/`，但提前创建也无副作用，可让首次运行更可控。

### 8. 架构与依赖方向

单向导入，无循环依赖：

```text
config.py ─┐
db.py ─────┼──> agents.py ──> teams.py ──────┐
tools.py ──┘                └─> workflows.py ─┼──> main.py
                                                │
                              agno.os.AgentOS <─┘
```

- `config.py` 为每个智能体返回**全新**的模型实例，避免共享客户端状态。
- `db.py` 暴露唯一的共享 `SqliteDb`，供所有 Agent、Team、Workflow 使用。
- `agents.py` 同时定义直接注册到 AgentOS 的智能体，以及供 Team/Workflow 使用的内部专家。
- `teams.py` / `workflows.py` 可以导入 agents，反之不行。
- `main.py` 是唯一构造 `AgentOS` 并启动服务的模块。

### 9. 已注册组件

组件 ID 由 `agno.utils.string.generate_id_from_name(name)` 自动生成：
转为小写，并把空格和下划线替换为 `-`。

#### 9.1 Agents

| 变量 | Agent ID | 模型 | 是否注册到 AgentOS | 关键特性 |
| --- | --- | --- | --- | --- |
| `basicAgent` | `basic-agent` | `deepseek-chat` | 是 | 计算器 + 只读 `FileTools` + 三种 HITL 工具；记忆更新、历史（5 轮）、时间上下文、markdown |
| `memoryAgent` | `memory-agent` | `deepseek-chat` | 是 | `MemoryManager` 抽取事实，并在后续运行中注入记忆 |
| `reasonAgent` | `reason-agent` | `deepseek-v4-flash` | 是 | `reasoning=True` 手动思维链，`reasoning_max_steps=5` |
| `structuredAgent` | `structured-agent` | `deepseek-chat` | 是 | `output_schema=ActionPlan`（`summary`、`steps`、`owner`） |
| `researcherAgent` | `researcher-agent` | `deepseek-chat` | 否 | 为流水线生成基于事实的大纲 |
| `writerAgent` | `writer-agent` | `deepseek-chat` | 否 | 撰写/修订 markdown，完成时输出 `READY TO PUBLISH` |
| `criticAgent` | `critic-agent` | `deepseek-chat` | 否 | 评审风险与缺口，也负责生成缓解方案 |
| `billingAgent` | `billing-agent` | `deepseek-chat` | 否 | 路由团队/工作流的账单专家 |
| `techAgent` | `technical-agent` | `deepseek-chat` | 否 | 路由团队/工作流的技术专家 |

#### 9.2 Teams

| 变量 | Team ID | 模式 | 成员 | 行为 |
| --- | --- | --- | --- | --- |
| `team` | `my-team` | `coordinate`（默认） | `basicAgent`、`reasonAgent` | 协调者分派任务、共享成员交互并汇总最终答案 |
| `supportTeam` | `support-team` | `TeamMode.route` | `billingAgent`、`techAgent` | 协调者只选择一个专家，并直接返回该专家的答案 |

`TeamMode.route` 必须使用枚举而不是字符串 `"route"`；AgentOS 会通过 `mode.value`
序列化团队模式。

#### 9.3 Workflows

| 变量 | Workflow ID | 组成 |
| --- | --- | --- |
| `researchPipeline` | `research-pipeline` | `Step` → `Parallel` → `Condition` → 执行器步骤 → `Loop` → 带 `HumanReview` 的 `Step` |
| `supportRouterWorkflow` | `support-router` | 单个 `Router`，选择 `billing` 或 `technical` 步骤 |

研究流水线：

```text
research（researcherAgent）
   │
   ├── draft        （writerAgent）   ─┐  Parallel
   └── risk-review  （criticAgent）   ─┘
   │
risk-gate（Condition：inputMentionsRisk）
   ├── 有风险 → mitigation-plan（criticAgent）
   └── 无风险 → no-risk-note   （执行器）
   │
assemble（执行器：assembleDraft —— 重建完整上下文）
   │
refine（Loop，max_iterations=2，出现 "READY TO PUBLISH" 时提前结束）
   │
publish（执行器：publishReport + HumanReview，拒绝时 OnReject.cancel）
   │
PUBLISHED ...
```

风险关键词为 `risk`、`security`、`compliance`、`风险`、`安全`、`合规`
（不区分大小写）。

支持路由：

```text
工单
  │
ticket-router（选择器：routeTicket）
  ├── 包含 invoice/refund/billing/账单/退款 → billingAgent
  └── 其他情况                             → techAgent
```

### 10. 工具与人在回路（HITL）

[`tools.py`](tools.py) 定义了：

| 工具 | 类型 | 行为 |
| --- | --- | --- |
| `calculator` | `CalculatorTools()` | 让模型用计算器做算术，而不是猜测 |
| `runbookReader` | `FileTools(base_dir="data")` | 只能读取/搜索 `data/`；保存、删除、分块替换均已禁用 |
| `delete_user_data` | `@approval` + `requires_confirmation=True` | 暂停运行，等待管理员审批 |
| `escalate_to_human` | `requires_user_input=True`，字段 `ticket_id` | 暂停运行，由操作员提供 `ticket_id` |
| `deploy_release` | `external_execution=True` | 暂停运行，由调用方在智能体进程之外执行并返回结果 |

暂停/恢复流程：

1. 智能体在执行工具前停下，返回状态为 **paused** 的运行结果。
2. 在运行输出中查看待处理需求（工具名、参数、审批 ID、用户输入 schema）。
3. 通过下面任一方式满足需求。
4. 使用相同的 `run_id` 和 `session_id` 调用 `continue` 端点，智能体从暂停处继续。

| HITL 模式 | 解决方式 | 恢复载荷 |
| --- | --- | --- |
| 管理员审批（`delete_user_data`） | `POST /approvals/{approval_id}/resolve`，请求体 `{"status": "approved"}` | `/continue` 只需 `session_id`（`tools` 可为空） |
| 用户输入（`escalate_to_human`） | 提供字段值 | `/continue` 的 `tools` JSON 中携带 `user_input_schema` 值，并设置 `answered: true` |
| 外部执行（`deploy_release`） | 由你自己执行部署动作 | `/continue` 的 `tools` JSON 中携带该工具的 `result` |

工作流级 HITL：[`workflows.py`](workflows.py) 在 `publish` 步骤上挂载了 `HumanReview`。
工作流会在发布前暂停，并通过
`POST /workflows/research-pipeline/runs/{run_id}/continue` 恢复。

### 11. 记忆、历史与持久化

- 所有已注册的 Agent、Team、Workflow 共享 `db = SqliteDb("data/agentos.db")`。
- 数据库保存会话、运行记录、消息、用户记忆和审批记录。
- `data/*` 已被 gitignore：删除 `data/agentos.db` 即可重置所有状态。
- 历史/上下文配置：
  - `basicAgent`：`add_history_to_context=True`、`num_history_runs=5`、
    `add_datetime_to_context=True`。
  - `memoryAgent`：`memory_manager=MemoryManager(...)`、`update_memory_on_run=True`、
    `add_memories_to_context=True`。
  - `reasonAgent`：`update_memory_on_run=True`、`add_history_to_context=True`。
- `runbookReader` 的 `base_dir` 相对于工作目录解析 —— 请在仓库根目录启动应用，
  这样它指向 `./data`。

### 12. API

#### 12.1 AgentOS REST 路由

路由没有 `/agno` 前缀。

| 资源 | 路由 |
| --- | --- |
| Agents | `GET /agents`、`GET /agents/{agent_id}`、`POST /agents/{agent_id}/runs`、`POST /agents/{agent_id}/runs/{run_id}/continue`、`POST /agents/{agent_id}/runs/{run_id}/cancel`、`POST /agents/{agent_id}/runs/{run_id}/resume`、`GET /agents/{agent_id}/runs`、`GET /agents/{agent_id}/runs/{run_id}` |
| Teams | `GET /teams`、`GET /teams/{team_id}`、`POST /teams/{team_id}/runs`、`POST /teams/{team_id}/runs/{run_id}/continue`、`POST /teams/{team_id}/runs/{run_id}/cancel`、`POST /teams/{team_id}/runs/{run_id}/resume`、`GET /teams/{team_id}/runs`、`GET /teams/{team_id}/runs/{run_id}` |
| Workflows | `GET /workflows`、`GET /workflows/{workflow_id}`、`POST /workflows/{workflow_id}/runs`、`POST /workflows/{workflow_id}/runs/{run_id}/continue`、`POST /workflows/{workflow_id}/runs/{run_id}/cancel`、`POST /workflows/{workflow_id}/runs/{run_id}/resume`、`GET /workflows/{workflow_id}/runs`、`GET /workflows/{workflow_id}/runs/{run_id}` |
| Sessions | `GET /sessions`、`POST /sessions`、`GET /sessions/{session_id}`、`GET /sessions/{session_id}/runs`、`GET /sessions/{session_id}/runs/{run_id}`、`POST /sessions/{session_id}/rename` 等 |
| Approvals | `GET /approvals`、`GET /approvals/count`、`GET /approvals/{approval_id}`、`GET /approvals/{approval_id}/status`、`POST /approvals/{approval_id}/resolve`、`DELETE /approvals/{approval_id}` |

**重要：** 运行类请求使用 `multipart/form-data`（FastAPI `Form` 字段），不是 JSON：

| 字段 | 默认值 | 含义 |
| --- | --- | --- |
| `message` | 必填 | 用户输入 |
| `stream` | `true` | 是否使用 SSE 流式响应；设为 `false` 可获得单个 JSON 响应 |
| `session_id` | 自动 | 会话连续性 / 恢复句柄 |
| `user_id` | 无 | 记忆归属与运行归属 |
| `background` | `false` | 后台运行，稍后通过 `/resume` 重连 |

#### 12.2 AG-UI 端点

| 前缀 | 目标 |
| --- | --- |
| `/endpoint/basic` | `basicAgent` |
| `/endpoint/reason` | `reasonAgent` |
| `/endpoint/team` | `team`（`my-team`） |

这些端点使用 AG-UI 协议，可对接 CopilotKit 等前端客户端。

#### 12.3 调用示例

列出 Agent：

```bash
curl -s http://localhost:7777/agents | python -m json.tool
```

运行 Agent（非流式，便于查看结果）：

```bash
curl -s -X POST http://localhost:7777/agents/basic-agent/runs \
  -F 'message=用计算器计算 1234 * 5678' \
  -F 'stream=false' \
  -F 'user_id=demo' \
  -F 'session_id=demo-session-1'
```

流式调用推理 Agent：

```bash
curl -N -X POST http://localhost:7777/agents/reason-agent/runs \
  -F 'message=为一次失败的数据库迁移设计回滚方案。' \
  -F 'stream=true' \
  -F 'user_id=demo'
```

请求结构化输出：

```bash
curl -s -X POST http://localhost:7777/agents/structured-agent/runs \
  -F 'message=规划新计费服务商的上线方案。' \
  -F 'stream=false'
```

运行协调团队：

```bash
curl -s -X POST http://localhost:7777/teams/my-team/runs \
  -F 'message=总结 42 * 17 的结果，并解释为什么结果可信。' \
  -F 'stream=false'
```

运行路由团队：

```bash
curl -s -X POST http://localhost:7777/teams/support-team/runs \
  -F 'message=账单 8842 被重复扣款了，请退回一笔。' \
  -F 'stream=false'
```

运行研究流水线（加入风险关键词可触发缓解分支）：

```bash
curl -s -X POST http://localhost:7777/workflows/research-pipeline/runs \
  -F 'message=写一份本服务选用 SQLite 与 Postgres 的对比报告，包含安全与合规风险。' \
  -F 'stream=false' \
  -F 'user_id=demo'
```

运行支持路由工作流：

```bash
curl -s -X POST http://localhost:7777/workflows/support-router/runs \
  -F 'message=轮换 API Key 后接口一直返回 401。' \
  -F 'stream=false'
```

查看待处理审批：

```bash
curl -s http://localhost:7777/approvals | python -m json.tool
```

解决审批并恢复暂停的 Agent 运行：

```bash
curl -s -X POST http://localhost:7777/approvals/<approval_id>/resolve \
  -H 'Content-Type: application/json' \
  -d '{"status": "approved", "resolved_by": "admin"}'
```

```bash
curl -s -X POST http://localhost:7777/agents/basic-agent/runs/<run_id>/continue \
  -F 'session_id=<session_id>' \
  -F 'stream=false'
```

通过 `tools` JSON 数组提供用户输入或外部执行结果；数组元素遵循
`agno.models.response.ToolExecution`（`tool_call_id`、`tool_name`、`tool_args`、
`result`、`user_input_schema`、`answered` 等）：

```bash
curl -s -X POST http://localhost:7777/agents/basic-agent/runs/<run_id>/continue \
  -F 'session_id=<session_id>' \
  -F 'tools=[{"tool_call_id":"<id>","tool_name":"escalate_to_human","user_input_schema":[{"name":"ticket_id","field_type":"str","value":"TCK-123"}]}]' \
  -F 'stream=false'
```

工作流在 `publish` 步骤暂停后，可回传其 `step_requirements` 并把确认状态改为已确认来恢复：

```bash
curl -s -X POST http://localhost:7777/workflows/research-pipeline/runs/<run_id>/continue \
  -F 'session_id=<session_id>' \
  -F 'step_requirements=[{"step_id":"<id>","step_name":"publish","requires_confirmation":true,"confirmed":true}]' \
  -F 'stream=false'
```

> 准确的 `step_id` 与需求结构来自暂停响应；原样复制后设置 `confirmed: true`
> （其他模式则填写 `user_input` / `selected_choices`）再回传即可。
> Web UI 或 Agno 客户端 SDK 会自动完成这一过程。

### 13. 实现说明

- **团队模式必须用枚举。** `TeamMode.route` 不能写成字符串 `"route"`，因为 AgentOS
  会用 `mode.value` 序列化。
- **容器步骤的载荷。** `Condition`、`Loop`、`Router` 只会在 `.content` 中放一行状态，
  真正的输出在 `.steps` 中 —— 因此 `assembleDraft` 和 `publishReport` 会用
  `collectText` 递归展平输出树。
- **循环终止条件。** `refinementComplete` 检查最后一条输出是否包含
  `READY TO PUBLISH`；否则在 `max_iterations=2` 时停止。
- **拒绝发布。** `OnReject.cancel` 表示拒绝 `publish` 步骤会取消整个工作流，
  而不是跳过该步骤。
- **迭代输出传递。** `forward_iteration_output=True` 让每次修订都能看到上一次的输出。
- **只读文件访问。** `runbookReader` 禁用了保存/删除/分块替换，并被限制在 `data/`。
- **关闭追踪。** `AgentOS(..., tracing=False)`；如需把追踪写入数据库可改为 `True`。
- **无知识库。** 显式传入 `knowledge=None`。

### 14. 开发

```bash
uv sync                       # 安装/刷新依赖
uv run main.py                # 以 reload=True 开发模式运行
source .venv/bin/activate     # 可选：进入普通 python shell
sh scripts/init.sh            # 删除 .venv/__pycache__，重建虚拟环境并 uv sync
```

仓库中**没有**配置测试套件、linter 或 formatter。

约定：

- 顶层扁平模块，不使用包结构。
- 导入方向单向：`config` / `db` / `tools` → `agents` → `teams` / `workflows` → `main`。
- 实例名使用 camelCase（`basicAgent`、`researchPipeline`、`agent_os`）。
- 提交信息使用 emoji 前缀 + 祈使句：`✨ add ...`、`➕ add ...`、`🎉 Init`。
- 永不提交 `.venv/`、`__pycache__/`、`data/*`。

### 15. 常见问题

| 现象 | 可能原因 / 解决方式 |
| --- | --- |
| 缺少 `DEEPSEEK_API_KEY` / 模型 API 返回 401 | 在运行 `uv run main.py` 的同一个 shell 中导出 Key。 |
| 模型不存在（如 `deepseek-v4-flash`） | 你的账号可能未开放该 ID；修改 `config.py` / `agents.py`。 |
| 读取 `data` 文件时报 `FileNotFoundError` | 在仓库根目录启动，并 `mkdir -p data`；把 runbook 文件放进 `data/`。 |
| 7777 端口被占用 | 停止占用进程，或在 `agent_os.serve(...)` 中指定其他端口。 |
| 测试时残留旧会话/记忆 | 删除 `data/agentos.db`（会清除所有本地状态）。 |
| 审批 resolve 返回 `409` | 该审批已被处理；先查询状态。 |
| `/continue` 返回 `409` | 运行不处于暂停状态（已在运行/已完成/已出错）。 |
| Python 版本错误 | `uv python install 3.14`，或删除 `.venv` 后重新 `uv sync`。 |

### 16. 限制说明

这是一个**演示项目**，并非生产部署：

- 默认未启用身份认证与授权。
- SQLite 是本地单文件数据库。
- 提示词与指令刻意保持简短。
- HITL 处理接口直接暴露在 HTTP 上；对外提供服务前必须置于真实的身份与授权体系之后。
- 删除 `data/` 或 SQLite 文件会永久移除会话、记忆和审批记录。
