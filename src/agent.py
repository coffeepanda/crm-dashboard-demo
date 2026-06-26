from __future__ import annotations

from pathlib import Path
from typing import Any

from aethergraph import NodeContext, graph_fn

from src.react.loop import run_react_loop

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def load_system_prompt() -> str:
    system = (PROMPT_DIR / "system.md").read_text(encoding="utf-8")
    tool_policy = (PROMPT_DIR / "tool_policy.md").read_text(encoding="utf-8")
    return f"{system}\n\n{tool_policy}"


@graph_fn(
    name="crm_dashboard_agent",
    inputs=["message", "chat_history", "session_id", "user_meta"],
    outputs=["reply"],
    as_agent={
        "id": "crm_dashboard_agent",
        "title": "CRM Dashboard",
        "short_description": "Answers questions about demo sales metrics.",
        "description": "Backend-only AetherGraph demo agent for numeric CRM-style dashboard questions.",
        "icon": "bar-chart-3",
        "color": "emerald",
        "session_kind": "chat",
        "mode": "chat_v1",
    },
)
async def crm_dashboard_agent(
    message: str,
    chat_history: list[dict[str, Any]] | None = None,
    session_id: str | None = None,
    user_meta: dict[str, Any] | None = None,
    *,
    context: NodeContext,
) -> dict[str, str]:
    reply = await run_react_loop(
        message=message,
        chat_history=chat_history or [],
        context=context,
        system_prompt=load_system_prompt(),
    )
    return {"reply": reply}
