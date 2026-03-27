#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then launches nanobot gateway.
"""

import json
import os
import sys
from pathlib import Path


def resolve_config():
    """Read config.json, inject env vars, write resolved config."""
    config_path = Path("/app/nanobot/config.json")
    resolved_path = Path("/app/nanobot/config.resolved.json")
    workspace_path = Path("/app/nanobot/workspace")

    if not config_path.exists():
        print(f"Error: config.json not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # Resolve LLM provider API key and base URL from env vars
    llm_api_key = os.environ.get("LLM_API_KEY", "")
    llm_base_url = os.environ.get("LLM_API_BASE_URL", "")
    llm_model = os.environ.get("LLM_API_MODEL", "")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_base_url:
        config["providers"]["custom"]["apiBase"] = llm_base_url
    if llm_model:
        config["agents"]["defaults"]["model"] = llm_model

    # Resolve gateway host/port from env vars
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "")

    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)

    # Resolve webchat channel config from env vars
    webchat_address = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "")
    access_key = os.environ.get("NANOBOT_ACCESS_KEY", "")

    if "webchat" not in config["channels"]:
        config["channels"]["webchat"] = {}

    if webchat_address:
        config["channels"]["webchat"]["host"] = webchat_address
    if webchat_port:
        config["channels"]["webchat"]["port"] = int(webchat_port)
    if access_key:
        config["channels"]["webchat"]["accessKey"] = access_key

    # Enable webchat channel
    config["channels"]["webchat"]["enabled"] = True
    config["channels"]["webchat"]["allowFrom"] = ["*"]

    # Resolve MCP server env vars (backend URL and API key)
    if "mcpServers" in config["tools"]:
        if "lms" in config["tools"]["mcpServers"]:
            lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL", "")
            lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY", "")

            if lms_backend_url:
                config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
            if lms_api_key:
                config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Resolved config written to {resolved_path}")

    # Launch nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", str(resolved_path), "--workspace", str(workspace_path)])


if __name__ == "__main__":
    resolve_config()
