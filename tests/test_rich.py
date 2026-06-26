import asyncio

from src.ui.rich import normalize_rich_card, send_finish, validate_rich_card


class FakeChannel:
    def __init__(self):
        self.texts = []
        self.rich = []

    async def send_text(self, text, **_kwargs):
        self.texts.append(text)

    async def send_rich(self, text=None, *, rich=None, **_kwargs):
        self.rich.append({"text": text, "rich": rich})


def _vega_spec():
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": [{"month": "2026-01", "revenue": 1}]},
        "mark": "bar",
        "encoding": {
            "x": {"field": "month", "type": "ordinal"},
            "y": {"field": "revenue", "type": "quantitative"},
        },
    }


def test_validate_rich_card_accepts_plot_block():
    ok, error = validate_rich_card(
        {
            "kind": "plot",
            "title": "Revenue",
            "payload": {"engine": "vega-lite", "spec": _vega_spec()},
        }
    )

    assert ok
    assert error is None


def test_validate_rich_card_accepts_blocks_wrapper():
    ok, error = validate_rich_card(
        {
            "blocks": [
                {
                    "kind": "plot",
                    "title": "Revenue",
                    "payload": {"engine": "vega-lite", "spec": _vega_spec()},
                }
            ]
        }
    )

    assert ok
    assert error is None


def test_normalize_rich_card_converts_direct_vega_lite_shape():
    normalized = normalize_rich_card(
        {
            "kind": "vega-lite",
            "title": "Revenue",
            "spec": _vega_spec(),
        }
    )

    assert normalized["kind"] == "plot"
    assert normalized["payload"]["engine"] == "vega-lite"


def test_send_finish_sends_normalized_rich_block():
    channel = FakeChannel()

    asyncio.run(
        send_finish(
            channel,
            text="Chart",
            card={"kind": "vega-lite", "title": "Revenue", "spec": _vega_spec()},
        )
    )

    assert channel.texts == []
    assert channel.rich[0]["rich"]["kind"] == "plot"
