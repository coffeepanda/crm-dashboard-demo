from __future__ import annotations

from typing import Any


def normalize_rich_card(card: Any) -> Any:
    """Normalize common LLM-produced rich payload variants to AG UI block shape."""
    if card is None:
        return None
    if isinstance(card, list):
        return {"blocks": [normalize_rich_card(block) for block in card]}
    if not isinstance(card, dict):
        return card

    if isinstance(card.get("blocks"), list):
        return {
            **card,
            "blocks": [normalize_rich_card(block) for block in card["blocks"]],
        }

    kind = card.get("kind")
    if kind == "vega-lite" and isinstance(card.get("spec"), dict):
        return {
            "kind": "plot",
            "title": card.get("title"),
            "payload": {"engine": "vega-lite", "spec": card["spec"]},
        }
    if card.get("engine") == "vega-lite" and isinstance(card.get("spec"), dict):
        return {
            "kind": "plot",
            "title": card.get("title"),
            "payload": {"engine": "vega-lite", "spec": card["spec"]},
        }
    return card


def validate_rich_card(card: Any) -> tuple[bool, str | None]:
    if card is None:
        return True, None
    if not isinstance(card, dict):
        return False, "card must be an object or null"

    if "blocks" in card:
        blocks = card.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            return False, "card.blocks must be a non-empty list"
        for index, block in enumerate(blocks):
            ok, error = validate_rich_card(block)
            if not ok:
                return False, f"card.blocks[{index}]: {error}"
        return True, None

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
    normalized_card = normalize_rich_card(card)
    ok, error = validate_rich_card(normalized_card)
    if normalized_card is not None and ok:
        await channel.send_rich(text=text, rich=normalized_card)
        return True, None
    await channel.send_text(text)
    return ok, error
