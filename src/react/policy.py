from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from .types import ToolCall

MAX_REACT_CYCLES = 5
MAX_REPEATED_CALLS = 3

MAX_CYCLE_MESSAGE = (
    "I could not complete the analysis within the tool-call limit for this turn. "
    "Try asking for one metric, time range, or grouping at a time."
)

REPEATED_CALL_MESSAGE = (
    "I got stuck repeating the same data request, so I stopped this turn instead of looping. "
    "Try rephrasing the question or narrowing the metric/time range."
)


@dataclass
class LoopPolicy:
    max_cycles: int = MAX_REACT_CYCLES
    max_repeated_calls: int = MAX_REPEATED_CALLS
    calls: Counter[str] = field(default_factory=Counter)

    def record_call(self, call: ToolCall) -> str | None:
        key = canonical_call_key(call)
        self.calls[key] += 1
        if self.calls[key] >= self.max_repeated_calls:
            return REPEATED_CALL_MESSAGE
        return None

    def cycle_stop_message(self, cycle_index: int) -> str | None:
        if cycle_index >= self.max_cycles:
            return MAX_CYCLE_MESSAGE
        return None


def canonical_call_key(call: ToolCall) -> str:
    args = dict(call.args)
    if call.tool == "query" and isinstance(args.get("sql"), str):
        args["sql"] = " ".join(args["sql"].split()).lower()
    return json.dumps({"tool": call.tool, "args": args}, sort_keys=True, ensure_ascii=False)
