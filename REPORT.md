# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Question: "What is the agentic loop?"**

The agentic loop is the fundamental cycle that autonomous AI agents follow to accomplish tasks. It typically consists of these core stages:

1. **Perceive** — Gather information from the environment (user input, files, APIs, sensors, etc.)
2. **Reason/Plan** — Analyze the information, determine goals, and decide on actions
3. **Act** — Execute actions using available tools (file operations, API calls, commands, etc.)
4. **Observe** — Receive feedback from the actions taken (outputs, errors, state changes)
5. **Reflect/Iterate** — Evaluate results, adjust the plan if needed, and continue the loop

This loop continues until the task is complete or a stopping condition is met. The key difference from a simple request-response model is that agents can autonomously iterate through this loop, making decisions and taking multiple actions without constant human guidance.

**Question: "What labs are available in our LMS?"**

The bare agent (without MCP tools) responded by reading from the workspace documentation files, describing the Lab 8 tasks and overview rather than returning actual backend data. This confirms the agent had no tools connected yet.

## Task 1B — Agent with LMS tools

**Question: "What labs are available?"**

With MCP tools connected, the agent returned real data from the backend:

| ID | Lab Title |
|----|-----------|
| 1 | Lab 01 – Products, Architecture & Roles |
| 2 | Lab 02 — Run, Fix, and Deploy a Backend Service |
| 3 | Lab 03 — Backend API: Explore, Debug, Implement, Deploy |
| 4 | Lab 04 — Testing, Front-end, and AI Agents |
| 5 | Lab 05 — Data Pipeline and Analytics Dashboard |
| 6 | Lab 06 — Build Your Own Agent |
| 7 | Lab 07 — Build a Client with an AI Coding Agent |
| 8 | lab-08 (The Agent is the Interface) ← Current lab |

**Question: "Describe the architecture of the LMS system"**

The agent provided a comprehensive architecture description including:

- **System Overview**: Caddy reverse proxy (port 42002) as single entry point, serving React SPA, FastAPI backend, and Nanobot agent
- **Core Services**: Caddy, FastAPI Backend (Python/SQLModel/Uvicorn), PostgreSQL, pgAdmin, Nanobot Agent, Qwen Code API
- **Observability Stack**: OpenTelemetry Collector, VictoriaLogs, VictoriaTraces
- **Data Model (OBER-based)**: Item (4-level hierarchy), Learner, Interacts tables
- **API Structure**: Items, Interactions, Learners routers with feature flags
- **Key Design Decisions**: Monolith with layered structure, Caddy as single entry point, SQLModel ORM, async database access, feature flags, standalone WebSocket relay
- **Deployment**: All services in Docker containers on lms-network

## Task 1C — Skill prompt

**Question: "Show me the scores" (without specifying a lab)**

With the skill prompt configured, the agent automatically:
1. Queried completion rates for all labs
2. Retrieved average scores by task for Labs 04-07
3. Listed top learners for Labs 04 and 07
4. Provided key insights

The response included formatted tables showing:
- Completion rates by lab (Lab 07 highest at 99.6%, Lab 08 at 0% as it just started)
- Average scores per task with attempt counts
- Top 5 learners per lab with their scores
- Key insight: Lab 06 Task 3 ("The System Agent") has the most attempts (2051) but lowest avg score (42.8%)

## Task 2A — Deployed agent

**Nanobot gateway startup log:**

```
nanobot-1  | Resolved config written to /app/nanobot/config.resolved.json
nanobot-1  | Using config: /app/nanobot/config.resolved.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | 2026-03-27 10:57:34.846 | INFO     | nanobot.channels.manager:_init_channels:54 - WebChat enabled
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | 2026-03-27 10:57:35.199 | INFO     | nanobot_webchat.channel:start:72 - Web Chat starting on 0.0.0.0:8765
nanobot-1  | 2026-03-27 10:57:36.701 | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:162 - MCP: registered tool 'mcp_lms_lms_health' from server 'lms'
nanobot-1  | 2026-03-27 10:57:36.702 | INFO     | nanobot.agent.tools.mcp:connect_mcp_servers:182 - MCP server 'lms': connected, 9 tools registered
nanobot-1  | 2026-03-27 10:57:36.702 | INFO     | nanobot.agent.loop:run:260 - Agent loop started
```

The gateway started successfully with:
- WebChat channel enabled on port 8765
- MCP server 'lms' connected with 9 tools registered (lms_health, lms_labs, lms_learners, lms_pass_rates, lms_timeline, lms_groups, lms_top_learners, lms_completion_rate, lms_sync_pipeline)
- Agent loop running

## Task 2B — Web client

**WebSocket endpoint test:**

The WebSocket endpoint at `ws://localhost:42002/ws/chat?access_key=vywYrALy228` is working. Logs show successful connections and message processing:

```
nanobot-1  | 2026-03-27 10:59:16.293 | INFO     | nanobot_webchat.channel:_handle_ws:120 - WebChat: new connection chat_id=5e2a16d3-0ce0-4129-9b79-2f7ecf9ac6e0
nanobot-1  | 2026-03-27 10:59:16.294 | INFO     | nanobot.agent.loop:_process_message:385 - Processing message from webchat:5e2a16d3-0ce0-4129-9b79-2f7ecf9ac6e0: What labs are available?
nanobot-1  | 2026-03-27 10:59:20.880 | INFO     | nanobot.agent.loop:_run_agent_loop:227 - Tool call: mcp_lms_lms_labs({})
nanobot-1  | 2026-03-27 10:59:26.933 | INFO     | nanobot.agent.loop:_process_message:452 - Response to webchat:5e2a16d3-0ce0-4129-9b79-2f7ecf9ac6e0: Here are the available labs:
```

**Flutter web client:**

Accessible at http://localhost:42002/flutter/ - the login screen loads correctly and accepts the NANOBOT_ACCESS_KEY for authentication.

## Task 3A — Structured logging

**Happy-path log excerpt (request with status 200):**

```
backend-1  | 2026-03-27 10:59:21,080 INFO [app.main] [main.py:60] [trace_id=7b154507c5bedf53486b8e1d8425f5ed span_id=5265698f06be365f resource.service.name=Learning Management Service trace_sampled=True] - request_started
backend-1  | 2026-03-27 10:59:21,184 INFO [app.auth] [auth.py:30] [trace_id=7b154507c5bedf53486b8e1d8425f5ed span_id=5265698f06be365f resource.service.name=Learning Management Service trace_sampled=True] - auth_success
backend-1  | 2026-03-27 10:59:21,211 INFO [app.db.items] [items.py:16] [trace_id=7b154507c5bedf53486b8e1d8425f5ed span_id=5265698f06be365f resource.service.name=Learning Management Service trace_sampled=True] - db_query
backend-1  | 2026-03-27 10:59:21,444 INFO [app.main] [main.py:68] [trace_id=7b154507c5bedf53486b8e1d8425f5ed span_id=5265698f06be365f resource.service.name=Learning Management Service trace_sampled=True] - request_completed
backend-1  | INFO:     172.20.0.9:34792 - "GET /items/ HTTP/1.1" 200
```

The log shows the full request lifecycle: `request_started` → `auth_success` → `db_query` → `request_completed` with HTTP 200.

**Error-path log excerpt (PostgreSQL stopped):**

```
backend-1  | 2026-03-27 11:07:39,569 INFO [app.main] [main.py:60] [trace_id=7a15eadb050ff638f411f4d49630a098 span_id=c89319b2d4661c3b resource.service.name=Learning Management Service trace_sampled=True] - request_started
backend-1  | 2026-03-27 11:07:39,570 INFO [app.auth] [auth.py:30] [trace_id=7a15eadb050ff638f411f4d49630a098 span_id=c89319b2d4661c3b resource.service.name=Learning Management Service trace_sampled=True] - auth_success
backend-1  | 2026-03-27 11:07:39,571 INFO [app.db.items] [items.py:16] [trace_id=7a15eadb050ff638f411f4d49630a098 span_id=c89319b2d4661c3b resource.service.name=Learning Management Service trace_sampled=True] - db_query
backend-1  | 2026-03-27 11:07:39,616 ERROR [app.db.items] [items.py:20] [trace_id=7a15eadb050ff638f411f4d49630a098 span_id=c89319b2d4661c3b resource.service.name=Learning Management Service trace_sampled=True] - db_query
backend-1  |   ... socket.gaierror: [Errno -2] Name or service not known
backend-1  | 2026-03-27 11:07:39,617 INFO [app.main] [main.py:68] [trace_id=7a15eadb050ff638f411f4d49630a098 span_id=c89319b2d4661c3b resource.service.name=Learning Management Service trace_sampled=True] - request_completed
backend-1  | INFO:     172.20.0.1:51618 - "GET /items/ HTTP/1.1" 404
```

The error log shows `db_query` with `ERROR` level and the exception `socket.gaierror: [Errno -2] Name or service not known` when PostgreSQL was unavailable.

**VictoriaLogs query:**

Query: `severity:ERROR`

Result shows structured JSON logs with fields like:
- `_msg`: "db_query"
- `severity`: "ERROR"
- `error`: "[Errno -2] Name or service not known"
- `event`: "db_query"
- `trace_id`: "7a15eadb050ff638f411f4d49630a098"

## Task 3B — Traces

**Healthy trace span hierarchy:**

A healthy trace shows the following span structure:
1. `GET /items/` (server span, duration: ~7ms, status: 200)
   - `connect` (database connection, ~106μs)
   - `SELECT db-lab-8` (database query, ~1.8ms)
   - `BEGIN;` (transaction start, ~294μs)
   - `GET /items/ http send` (response, ~32μs, status: 200)

**Error trace:**

When PostgreSQL was stopped, the error trace shows:
1. `GET /items/` (server span, duration: ~44ms, status: 404)
   - `connect` (database connection attempt, ~126μs)
   - `SELECT db-lab-8` (database query, ~23ms) - **ERROR: "connection is closed"**
   - Exception log with full stack trace: `socket.gaierror: [Errno -2] Name or service not known`

The error appears in the `SELECT db-lab-8` span with `error: true` tag and exception details in the span logs.

## Task 3C — Observability MCP tools

**New MCP tools implemented:**

| Tool | Description |
|------|-------------|
| `logs_search` | Search logs using LogsQL query |
| `logs_error_count` | Count errors per service over a time window |
| `traces_list` | List recent traces |
| `traces_get` | Fetch a specific trace by ID |
| `traces_services` | List all services with traces |

**Agent response under normal conditions:**

Question: "Any errors in the last hour?"

> "Yes, there are **4 errors** in the last hour, all from the **Learning Management Service**:
> 
> | Time | Error Type | Details |
> |------|------------|---------|
> | ... | db_query | [Errno -2] Name or service not known |
> 
> These errors occurred when the database connection failed. The system has since recovered."

**Agent response under failure conditions (PostgreSQL stopped):**

Question: "Any errors in the last hour?"

> "Yes, there are **5 errors** in the last hour, all from the **Learning Management Service**.
> 
> ## Error Summary
> 
> | Issue | Count |
> |-------|-------|
> | Database connection failures | 5 |
>
> ## Root Cause
>
> All errors show `socket.gaierror: [Errno -2] Name or service not known` when attempting to connect to PostgreSQL. This indicates the database service was unavailable.
>
> ## Recommendation
>
> Check if the PostgreSQL container is running: `docker compose ps postgres`"

## Task 4A — Multi-step investigation

**Agent's "What went wrong?" response with PostgreSQL stopped:**

The agent performed a one-shot investigation chaining logs and traces:

**Tool calls observed:**
1. `logs_search(query="/items/", limit=20)` - Search for logs related to the endpoint
2. `logs_error_count(minutes=60)` - Get error count overview
3. `traces_list(limit=15)` - List recent traces
4. `logs_search(query="severity:ERROR", limit=30)` - Find error logs
5. `lms_health()` - Check LMS backend health
6. `traces_get(trace_id="aec71d9df5a0ed14d6549cd061795ebb")` - Fetch specific trace

**Agent response:**
```
## Issue Found: Database Connection Failure

The `/items/` endpoint is failing due to a **database connectivity issue**.

### Evidence from Logs:
- Found multiple errors with `severity:ERROR` from the Learning Management Service
- Error type: `socket.gaierror`
- Error message: `[Errno -2] Name or service not known`
- The error occurs during database connection attempts

### Evidence from Traces:
- Trace ID: `aec71d9df5a0ed14d6549cd061795ebb`
- Failed span: `SELECT db-lab-8` (database query)
- The trace shows the request flow: request_started → auth_success → db_query → exception

### Root Cause:
The backend cannot connect to PostgreSQL because the database container is stopped. 
The error `Name or service not known` indicates DNS resolution failure for the `postgres` hostname.

### Recommendation:
1. Check if PostgreSQL is running: `docker compose ps postgres`
2. If stopped, restart it: `docker compose start postgres`
3. Verify connectivity after restart
```

## Task 4B — Proactive health check

**Creating a scheduled health check:**

The agent was asked to create a health check cron job that runs every 2 minutes. The agent used its built-in cron tool to schedule periodic checks that:
- Run `logs_error_count(minutes=2)` to check for recent errors
- If errors found, investigate with `logs_search` and `traces_get`
- Post a summary to the current chat

**Proactive health report (while PostgreSQL was stopped):**
```
## Health Check Report

**Status:** ⚠️ Issues Detected

**Time window:** Last 2 minutes

**Errors found:** 3 errors from Learning Management Service

**Root cause:** Database connection failures
- Error: `socket.gaierror: [Errno -2] Name or service not known`
- Affected endpoint: `/items/`

**Recommendation:** PostgreSQL container appears to be down. 
Run `docker compose start postgres` to restore service.
```

## Task 4C — Bug fix and recovery

### 1. Root Cause — Planted Bug Identified

**Location:** `backend/app/routers/items.py`, `get_items` endpoint

**Bug:** The endpoint caught all exceptions and returned a misleading HTTP 404 "Items not found" error instead of properly propagating database errors as HTTP 500.

```python
# BUGGY CODE:
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    """Get all items."""
    try:
        return await read_items(session)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Items not found",
        ) from exc  # ← Wrong! Database errors become 404s
```

**Impact:** When PostgreSQL was unavailable, the API returned `{"detail": "Items not found"}` with HTTP 404, masking the real database connectivity issue and making debugging difficult.

### 2. Fix Applied

**Change:** Removed the try-except wrapper that was catching and misrepresenting all exceptions.

```python
# FIXED CODE:
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    """Get all items."""
    return await read_items(session)  # ← Let exceptions propagate naturally
```

**Result:** Database errors now properly propagate as HTTP 500 with detailed error information via the global exception handler.

### 3. Post-Fix Failure Check

After the fix, with PostgreSQL stopped, the API now returns the actual error:

```json
{
  "detail": "[Errno -2] Name or service not known",
  "type": "gaierror",
  "path": "/items/",
  "traceback": [
    "  File \"/app/.venv/lib/python3.14/site-packages/asyncpg/connect_utils.py\", line 969, in _create_ssl_connection",
    "socket.gaierror: [Errno -2] Name or service not known"
  ]
}
```

The agent's "What went wrong?" response now correctly identifies:
- The actual exception type (`gaierror`)
- The real error message (`Name or service not known`)
- The root cause (PostgreSQL unavailable)

### 4. Healthy Follow-Up

After restarting PostgreSQL, the system is healthy:

**Agent health check report:**
```
## Health Check Report

**Status:** ✅ Healthy

**Time window:** Last 2 minutes

**Errors found:** 0

The system is operating normally. All endpoints responding with HTTP 200.
```

**API verification:**
```bash
$ curl http://localhost:42001/items/ -H "Authorization: Bearer api-key"
[{"title":"Lab 01 – Products, Architecture & Roles","id":1,...}, ...]
```
