from __future__ import annotations

from typing import Any


def vega_bar_chart(
    *,
    title: str,
    values: list[dict[str, Any]],
    x_field: str,
    y_field: str,
    x_type: str = "ordinal",
    y_type: str = "quantitative",
) -> dict[str, Any]:
    return {
        "kind": "plot",
        "title": title,
        "payload": {
            "engine": "vega-lite",
            "spec": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {"values": values},
                "mark": "bar",
                "encoding": {
                    "x": {"field": x_field, "type": x_type},
                    "y": {"field": y_field, "type": y_type},
                },
            },
        },
    }


def vega_line_chart(
    *,
    title: str,
    values: list[dict[str, Any]],
    x_field: str,
    y_field: str,
) -> dict[str, Any]:
    return {
        "kind": "plot",
        "title": title,
        "payload": {
            "engine": "vega-lite",
            "spec": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {"values": values},
                "mark": {"type": "line", "point": True},
                "encoding": {
                    "x": {"field": x_field, "type": "ordinal"},
                    "y": {"field": y_field, "type": "quantitative"},
                },
            },
        },
    }
