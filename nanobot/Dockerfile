# Multi-stage Dockerfile for nanobot gateway
# Adapted from backend/Dockerfile pattern

# ---
# Stage 1: Build the application
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
# Copy workspace-level files from parent context
COPY --from=workspace pyproject.toml uv.lock /app/
# Copy nanobot project files (build context is ./nanobot)
COPY pyproject.toml /app/nanobot/pyproject.toml

# Sync nanobot dependencies (without workspace members yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot

# Copy the rest of nanobot source
COPY . /app/nanobot/

# Copy workspace members that nanobot depends on
COPY --from=workspace mcp/ /app/mcp/
COPY --from=workspace nanobot-websocket-channel/ /app/nanobot-websocket-channel/

# Sync again to pick up local workspace members
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

# ---
# Stage 2: Final runtime image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/nanobot"

USER nonroot

WORKDIR /app/nanobot

# Run the entrypoint which resolves config and starts gateway
CMD ["python", "/app/nanobot/entrypoint.py"]
