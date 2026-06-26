from __future__ import annotations

from typing import Any


def metric_card(
    *,
    title: str,
    items: list[dict[str, Any]],
    right_text: str | None = None,
    tone: str = "info",
) -> dict[str, Any]:
    return {
        "kind": "component",
        "payload": {
            "component_type": "ag.ui.card.v1",
            "props": {
                "version": "card.v1",
                "header": {
                    "title": title,
                    "right_text": right_text,
                    "tone": tone,
                },
                "sections": [
                    {
                        "type": "kv",
                        "columns": 2,
                        "items": items,
                    }
                ],
            },
        },
    }
