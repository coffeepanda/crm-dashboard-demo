from __future__ import annotations

from typing import Any


def validate_rich_card(card: Any) -> tuple[bool, str | None]:
    if card is None:
        return True, None
    if not isinstance(card, dict):
        return False, "card must be an object or null"

    kind = card.get("kind")
    payload = card.get("payload")
    if kind == "component":
        if not isinstance(payload, dict):
            return False, "component card requires payload object"
        if payload.get("component_type") != "ag.ui.card.v1":
            return False, "component card must use ag.ui.card.v1"
        props = payload.get("props")
        if not isinstance(props, dict):
            return False, "component card requires props object"
        if props.get("version") != "card.v1":
            return False, "component card props.version must be card.v1"
        return True, None

    if kind == "plot":
        if not isinstance(payload, dict):
            return False, "plot card requires payload object"
        if payload.get("engine") != "vega-lite":
            return False, "plot card payload.engine must be vega-lite"
        if not isinstance(payload.get("spec"), dict):
            return False, "plot card requires a Vega-Lite spec object"
        return True, None

    return False, "card kind must be component or plot"


async def send_finish(channel: Any, *, text: str, card: Any = None) -> tuple[bool, str | None]:
    ok, error = validate_rich_card(card)
    if card is not None and ok:
        await channel.send_rich(text=text, rich=card)
        return True, None
    await channel.send_text(text)
    return ok, error
