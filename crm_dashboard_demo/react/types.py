from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolCall:
    """Validated JSON tool call produced by the LLM."""

    tool: str
    args: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    """Tool execution result shown back to the LLM in the ReAct context."""

    tool: str
    ok: bool
    error_code: str | None
    error: str | None
    args: dict[str, Any]
    result: dict[str, Any] | None
    hint: str | None = None

    def to_agent_dict(self, *, max_rows: int = 25) -> dict[str, Any]:
        result = self.result
        if result and isinstance(result.get("rows"), list):
            rows = result["rows"][:max_rows]
            result = {
                **result,
                "rows": rows,
                "rows_truncated": len(result["rows"]) > len(rows),
            }
        return {
            "tool": self.tool,
            "ok": self.ok,
            "error_code": self.error_code,
            "error": self.error,
            "args": self.args,
            "result": result,
            "hint": self.hint,
        }
