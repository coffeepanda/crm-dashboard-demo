from __future__ import annotations

from typing import Any

from src.tools.handler import handle_finish, handle_query, parse_tool_call
from src.tools.schemas import SCHEMA_SUMMARY, TOOL_SCHEMA_SUMMARY

from .context import compose_react_messages
from .policy import LoopPolicy, MAX_CYCLE_MESSAGE
from .types import ToolResult


async def run_react_loop(
    *,
    message: str,
    chat_history: list[dict[str, Any]] | None,
    context: Any,
    system_prompt: str,
) -> str:
    llm = context.llm()
    channel = context.channel("ui:session")
    policy = LoopPolicy()
    tool_results: list[ToolResult] = []

    for _cycle_index in range(policy.max_cycles):
        messages = compose_react_messages(
            system_prompt=system_prompt,
            schema_summary=SCHEMA_SUMMARY,
            tool_schema_summary=TOOL_SCHEMA_SUMMARY,
            chat_history=chat_history or [],
            user_message=message,
            tool_results=tool_results,
        )
        raw, _usage = await llm.chat(messages=messages, max_output_tokens=1800)
        call, parse_error = parse_tool_call(str(raw))
        if parse_error is not None:
            tool_results.append(parse_error)
            continue
        assert call is not None

        stop_message = policy.record_call(call)
        if stop_message:
            await channel.send_text(stop_message)
            return stop_message

        if call.tool == "query":
            tool_results.append(handle_query(call))
            continue

        if call.tool == "finish":
            finish_result, reply = await handle_finish(call, channel=channel)
            tool_results.append(finish_result)
            return reply

        tool_results.append(
            ToolResult(
                tool=call.tool,
                ok=False,
                error_code="unknown_tool",
                error="Unknown tool. Available tools are query and finish.",
                args=call.args,
                result=None,
                hint="Use query or finish.",
            )
        )

    await channel.send_text(MAX_CYCLE_MESSAGE)
    return MAX_CYCLE_MESSAGE
