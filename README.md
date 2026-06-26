# CRM Dashboard Demo

This is a backend-only AetherGraph demo that turns a small synthetic sales database into a chat-driven dashboard. The user asks natural-language questions about sales metrics, and the agent answers by using a tiny ReAct loop over two tools:

- `query`: run guarded read-only SQL against the demo SQLite database.
- `finish`: send the final text response, optionally with an AG UI rich card or Vega-Lite plot.

The demo is meant to exercise the AetherGraph agent path, AG UI chat surface, rich message rendering, and LLM-driven tool calls without relying on `aethergraph_engine`.

## Architecture

```text
AG UI chat
  -> crm_dashboard_agent @graph_fn
    -> context.llm() using the default LLM profile
    -> ReAct loop with chat history + current-turn ToolResults
      -> query tool
        -> SQL validator
        -> src/data/crm.sqlite
      -> finish tool
        -> context.channel("ui:session").send_text(...)
        -> context.channel("ui:session").send_rich(...)
```

Important implementation choices:

- The agent is a single `@graph_fn` in `src/agent.py`.
- All tool-call generation goes through `context.llm()`.
- There is no keyword routing, regex intent detection, or deterministic tool generation.
- The agent does not use AetherGraph memory yet; it relies on visible chat history and current-turn tool results.
- The UI communication path is turn-based only. The agent does not use `ask_*` channel methods.
- `src/data/crm.sqlite` is checked in so the demo works immediately after clone.

## Dependencies

Install AetherGraph:

```bash
pip install aethergraph
```

## Configure

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

The included `.env.example` uses the AetherGraph default LLM profile. I tested this demo with `gpt-5o-nano`. AetherGraph also supports other providers such as Anthropic and DeepSeek by changing the provider, model, base URL, and API key values.

## Start The Agent

From this folder:

```bash
aethergraph serve --project-root . --load-module src.agent --reload
```

The CLI keeps the AetherGraph server and UI running, and prints the local AG UI URL. Open that URL in your browser. Leave the command running while you test the agent, and stop it with `Ctrl+C`.

In the UI:

1. Click **Agent** in the left sidebar.
2. Select **CRM Dashboard**.
3. Start chatting with the agent.

The default runtime workspace is `aethergraph_workspace/`. It is generated locally and ignored by Git.

## Prompts To Try

- Show closed-won revenue by month as a chart.
- Which team has the highest quota attainment?
- Compare pipeline amount and forecast amount by region.
- Which accounts have the highest churn risk score?
- Show the top five reps by closed-won amount.
- What is the average sales cycle by segment?
- Which month had the best win rate?
- Summarize activity volume by team using meetings, calls, and emails.
- Which accounts have high expansion score but low customer health?
- Can you forecast NVIDIA stock next week?

The last prompt is intentionally out of scope. The agent should respond directly with `finish` instead of querying the database.

## Current Limitations And Known Bugs

- Vega-Lite plots render, but plot sizing is not always consistent in AG UI chat.
- There is no custom interactive dashboard component yet. The current rich output is limited to generic cards and Vega-Lite blocks; deeper interaction needs frontend work.
- The agent has no long-term memory. It only sees the chat history passed into the current run and the tool results from the current turn.
- The LLM may occasionally produce malformed card JSON. The backend now normalizes common Vega-Lite variants and falls back to text if the card is invalid.
- SQL support is intentionally narrow: read-only `SELECT` queries against `sales_metrics_enriched`.

## Future Work

- Add a dedicated interactive CRM dashboard component in AG UI for richer filtering, drill-down, and chart resizing.
- Add session memory so the agent can remember user preferences, previous metric selections, and prior analysis.
- Add deterministic chart builders as optional post-processing after successful queries, while keeping tool-call generation LLM-driven.
- Improve validation and repair prompts for Vega-Lite specs.
- Add more seeded metric domains, such as renewals, product usage, support volume, and expansion pipeline.
- Add snapshot tests or frontend smoke tests for rich card and Vega-Lite rendering.
