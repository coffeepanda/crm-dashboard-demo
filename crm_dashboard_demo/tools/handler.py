from __future__ import annotations

import json
import sqlite3
from typing import Any

from crm_dashboard_demo.db.repository import run_select_query
from crm_dashboard_demo.react.types import ToolCall, ToolResult
from crm_dashboard_demo.ui.rich import send_finish

from .validation import validate_select_sql


def parse_tool_call(raw: str) -> tuple[ToolCall | None, ToolResult | None]:
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, ToolResult(
            tool="unknown",
            ok=False,
            error_code="invalid_json",
            error=f"LLM response was not valid JSON: {exc.msg}",
            args={"raw": raw[:1000]},
            result=None,
            hint="Return exactly one JSON object with tool and args.",
        )

    if not isinstance(obj, dict):
        return None, ToolResult(
            tool="unknown",
            ok=False,
            error_code="invalid_json",
            error="Tool call must be a JSON object.",
            args={"value": obj},
            result=None,
            hint="Return an object like {\"tool\":\"query\",\"args\":{...}}.",
        )

    tool = obj.get("tool")
    args = obj.get("args")
    if tool not in {"query", "finish"}:
        return None, ToolResult(
            tool=str(tool or "unknown"),
            ok=False,
            error_code="unknown_tool",
            error="Unknown tool. Available tools are query and finish.",
            args=obj if isinstance(obj, dict) else {},
            result=None,
            hint="Use query for database facts or finish for user-facing output.",
        )
    if not isinstance(args, dict):
        return None, ToolResult(
            tool=str(tool),
            ok=False,
            error_code="invalid_args",
            error="Tool args must be an object.",
            args={"args": args},
            result=None,
            hint="Return args as a JSON object.",
        )
    return ToolCall(tool=str(tool), args=args), None


def handle_query(call: ToolCall) -> ToolResult:
    validation = validate_select_sql(call.args.get("sql"))
    if not validation.ok:
        return ToolResult(
            tool="query",
            ok=False,
            error_code=validation.error_code,
            error=validation.error,
            args=call.args,
            result=None,
            hint=validation.hint,
        )

    assert validation.sql is not None
    try:
        result = run_select_query(validation.sql)
    except sqlite3.OperationalError as exc:
        message = str(exc)
        error_code = "unknown_column" if "no such column" in message.lower() else "query_failed"
        return ToolResult(
            tool="query",
            ok=False,
            error_code=error_code,
            error=message,
            args={**call.args, "sql": validation.sql},
            result=None,
            hint="Use only documented columns from sales_metrics_enriched.",
        )
    except Exception as exc:
        return ToolResult(
            tool="query",
            ok=False,
            error_code="query_failed",
            error=str(exc),
            args={**call.args, "sql": validation.sql},
            result=None,
            hint="Try a simpler SELECT with fewer columns or groups.",
        )

    hint = "Use finish when you have enough data, or run another query for comparison."
    if result["row_count"] == 0:
        hint = "No rows matched. You can finish with that caveat or try a broader query."
    return ToolResult(
        tool="query",
        ok=True,
        error_code=None,
        error=None,
        args={**call.args, "sql": validation.sql},
        result=result,
        hint=hint,
    )


async def handle_finish(call: ToolCall, *, channel: Any) -> tuple[ToolResult, str]:
    text = call.args.get("text")
    card = call.args.get("card")
    if not isinstance(text, str) or not text.strip():
        text = "I could not produce a valid final response for this turn."
    ok, card_error = await send_finish(channel, text=text, card=card)
    if ok:
        return ToolResult(
            tool="finish",
            ok=True,
            error_code=None,
            error=None,
            args=call.args,
            result={"sent": "rich" if card is not None else "text"},
            hint=None,
        ), text

    return ToolResult(
        tool="finish",
        ok=False,
        error_code="invalid_card_schema",
        error=card_error,
        args=call.args,
        result={"sent": "text"},
        hint="The text was sent, but the rich card was ignored.",
    ), text
