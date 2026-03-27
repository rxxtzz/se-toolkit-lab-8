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

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
