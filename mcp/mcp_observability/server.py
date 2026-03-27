"""Stdio MCP server exposing VictoriaLogs and VictoriaTraces operations as typed tools."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("observability")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_victorialogs_url: str = ""
_victoriatraces_url: str = ""


def _resolve_victorialogs_url() -> str:
    return _victorialogs_url or os.environ.get("VICTORIALOGS_URL", "http://localhost:9428")


def _resolve_victoriatraces_url() -> str:
    return _victoriatraces_url or os.environ.get("VICTORIATRACES_URL", "http://localhost:10428")


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _LogsSearchQuery(BaseModel):
    query: str = Field(
        default="*",
        description="LogsQL query string (e.g., 'severity:ERROR', 'service.name:backend').",
    )
    limit: int = Field(default=10, ge=1, le=1000, description="Max log entries to return.")


class _LogsErrorCountQuery(BaseModel):
    service: str = Field(default="", description="Filter by service name (optional).")
    minutes: int = Field(default=60, ge=1, description="Time window in minutes.")


class _TracesListQuery(BaseModel):
    service: str = Field(default="", description="Filter by service name.")
    limit: int = Field(default=10, ge=1, le=100, description="Max traces to return.")


class _TracesGetQuery(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch.")


class _NoArgs(BaseModel):
    """Empty input model for tools that don't need parameters."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(data: Any) -> list[TextContent]:
    """Serialize data to a JSON text block."""
    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, default=str))]


# ---------------------------------------------------------------------------
# Tool handlers - VictoriaLogs
# ---------------------------------------------------------------------------


async def _logs_search(args: _LogsSearchQuery) -> list[TextContent]:
    """Search logs in VictoriaLogs using LogsQL."""
    url = f"{_resolve_victorialogs_url()}/select/logsql/query"
    params = {"query": args.query, "limit": args.limit}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        logs = []
        for line in lines:
            if line.strip():
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    logs.append({"raw": line})
    return _text(logs)


async def _logs_error_count(args: _LogsErrorCountQuery) -> list[TextContent]:
    """Count errors per service over a time window."""
    # Build query for errors
    query = "severity:ERROR"
    if args.service:
        query = f"{query} AND service.name:{args.service}"
    
    url = f"{_resolve_victorialogs_url()}/select/logsql/query"
    params = {"query": query, "limit": 1000}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
    
    # Count errors by service
    error_counts: dict[str, int] = {}
    for line in lines:
        if line.strip():
            try:
                log = json.loads(line)
                service = log.get("service.name", log.get("service", "unknown"))
                error_counts[service] = error_counts.get(service, 0) + 1
            except json.JSONDecodeError:
                pass
    
    result = [{"service": svc, "error_count": cnt} for svc, cnt in sorted(error_counts.items(), key=lambda x: -x[1])]
    return _text(result)


# ---------------------------------------------------------------------------
# Tool handlers - VictoriaTraces
# ---------------------------------------------------------------------------


async def _traces_list(args: _TracesListQuery) -> list[TextContent]:
    """List recent traces from VictoriaTraces."""
    url = f"{_resolve_victoriatraces_url()}/select/jaeger/api/traces"
    params = {"limit": args.limit}
    if args.service:
        params["service"] = args.service
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
    
    # Extract summary info from traces
    traces_data = data.get("data", [])
    summaries = []
    for trace in traces_data[: args.limit]:
        trace_id = trace.get("traceID", "unknown")
        spans = trace.get("spans", [])
        operations = list(set(span.get("operationName", "unknown") for span in spans))
        summaries.append(
            {
                "trace_id": trace_id,
                "span_count": len(spans),
                "operations": operations[:5],  # Limit operations shown
            }
        )
    return _text(summaries)


async def _traces_get(args: _TracesGetQuery) -> list[TextContent]:
    """Fetch a specific trace by ID."""
    url = f"{_resolve_victoriatraces_url()}/select/jaeger/api/traces/{args.trace_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=30.0)
        if resp.status_code == 404:
            return _text({"error": f"Trace {args.trace_id} not found"})
        resp.raise_for_status()
        data = resp.json()
    
    # Extract trace summary
    trace_data = data.get("data", [])
    if not trace_data:
        return _text({"error": f"Trace {args.trace_id} not found"})
    
    trace = trace_data[0]
    spans = trace.get("spans", [])
    
    # Build span hierarchy summary
    span_summary = []
    for span in spans:
        span_info = {
            "span_id": span.get("spanID", "unknown"),
            "operation": span.get("operationName", "unknown"),
            "duration_us": span.get("duration", 0),
            "has_error": any(
                tag.get("key") == "error" and tag.get("value") == "true"
                for tag in span.get("tags", [])
            ),
            "logs_count": len(span.get("logs", [])),
        }
        span_summary.append(span_info)
    
    return _text({"trace_id": args.trace_id, "spans": span_summary})


async def _traces_services(_args: _NoArgs) -> list[TextContent]:
    """List all services that have reported traces."""
    url = f"{_resolve_victoriatraces_url()}/select/jaeger/api/services"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=30.0)
        if resp.status_code == 404:
            # Fallback: query traces and extract unique services
            traces_url = f"{_resolve_victoriatraces_url()}/select/jaeger/api/traces?limit=100"
            resp = await client.get(traces_url, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            services = set()
            for trace in data.get("data", []):
                for span in trace.get("spans", []):
                    process_id = span.get("processID", "")
                    processes = trace.get("processes", {})
                    if process_id in processes:
                        svc = processes[process_id].get("serviceName", "unknown")
                        services.add(svc)
            return _text(sorted(services))
        resp.raise_for_status()
        return _text(resp.json())


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "logs_search",
    "Search logs in VictoriaLogs using LogsQL. Returns matching log entries.",
    _LogsSearchQuery,
    _logs_search,
)
_register(
    "logs_error_count",
    "Count errors per service over a time window. Returns service names and error counts.",
    _LogsErrorCountQuery,
    _logs_error_count,
)
_register(
    "traces_list",
    "List recent traces from VictoriaTraces. Returns trace summaries with operation names.",
    _TracesListQuery,
    _traces_list,
)
_register(
    "traces_get",
    "Fetch a specific trace by ID. Returns span hierarchy and error status.",
    _TracesGetQuery,
    _traces_get,
)
_register(
    "traces_services",
    "List all services that have reported traces.",
    _NoArgs,
    _traces_services,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except httpx.HTTPError as exc:
        return [TextContent(type="text", text=f"HTTP error: {type(exc).__name__}: {exc}")]
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main(victorialogs_url: str | None = None, victoriatraces_url: str | None = None) -> None:
    global _victorialogs_url, _victoriatraces_url
    _victorialogs_url = victorialogs_url or os.environ.get("VICTORIALOGS_URL", "")
    _victoriatraces_url = victoriatraces_url or os.environ.get("VICTORIATRACES_URL", "")
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
