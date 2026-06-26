from __future__ import annotations

import json
from typing import Any

from .types import ToolResult


def compact_json(value: Any, *, max_chars: int = 8000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 120] + "\n... [truncated for context budget]"


def compose_react_messages(
    *,
    system_prompt: str,
    schema_summary: str,
    tool_schema_summary: str,
    chat_history: list[dict[str, Any]],
    user_message: str,
    tool_results: list[ToolResult],
) -> list[dict[str, str]]:
    # ReAct context includes:
    # - immutable system/tool policy
    # - compact database schema and allowed query surface
    # - general JSON schemas for query and finish tool calls
    # - visible chat history provided to this graph_fn call
    # - latest user message
    # - all tool results produced during this turn
    #
    # It intentionally excludes persistent memory, hidden channel state,
    # deterministic intent routing, regex/keyword tool selection, and direct UI handles.
    safe_history: list[dict[str, Any]] = []
    for item in chat_history or []:
        role = str(item.get("role") or "user")
        if role not in {"user", "assistant", "system"}:
            role = "user"
        content = str(item.get("content") or item.get("text") or "")
        if content:
            safe_history.append({"role": role, "content": content})

    tool_context = [item.to_agent_dict() for item in tool_results]
    developer_context = (
        "Database schema and query surface:\n"
        f"{schema_summary}\n\n"
        "Available JSON tool call shapes:\n"
        f"{tool_schema_summary}\n\n"
        "Current-turn tool results:\n"
        f"{compact_json(tool_context)}"
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": developer_context},
    ]
    messages.extend(safe_history[-20:])
    messages.append({"role": "user", "content": user_message})
    return messages
