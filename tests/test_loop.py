import asyncio

from src.react.loop import run_react_loop


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.messages = []

    async def chat(self, *, messages, **_kwargs):
        self.messages.append(messages)
        return self.responses.pop(0), {}


class FakeChannel:
    def __init__(self):
        self.texts = []
        self.rich = []

    async def send_text(self, text, **_kwargs):
        self.texts.append(text)

    async def send_rich(self, text=None, *, rich=None, **_kwargs):
        self.rich.append({"text": text, "rich": rich})


class FakeContext:
    def __init__(self, llm, channel):
        self._llm = llm
        self._channel = channel

    def llm(self):
        return self._llm

    def channel(self, channel_key):
        assert channel_key == "ui:session"
        return self._channel


def test_react_loop_queries_then_finishes():
    asyncio.run(_run_react_loop_queries_then_finishes())


async def _run_react_loop_queries_then_finishes():
    llm = FakeLLM(
        [
            (
                '{"tool":"query","args":{"sql":"SELECT month, '
                'SUM(closed_won_amount) AS revenue FROM sales_metrics_enriched '
                'GROUP BY month ORDER BY month LIMIT 2","purpose":"trend",'
                '"expected_shape":"time_series"}}'
            ),
            '{"tool":"finish","args":{"text":"Revenue is available for the requested months.","card":null}}',
        ]
    )
    channel = FakeChannel()
    context = FakeContext(llm, channel)

    reply = await run_react_loop(
        message="Show revenue by month.",
        chat_history=[],
        context=context,
        system_prompt="system",
    )

    assert reply == "Revenue is available for the requested months."
    assert channel.texts == ["Revenue is available for the requested months."]
    assert "Current-turn tool results" in llm.messages[1][1]["content"]
