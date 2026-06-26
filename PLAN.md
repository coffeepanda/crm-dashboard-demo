# CRM Dashboard Demo Plan

## Goal

Build a backend-only AetherGraph dashboard demo where a single ReAct-style agent answers questions about a fake numeric sales database. The agent will use AetherGraph backend primitives only, not `aethergraph_engine`.

The demo should feel like a lightweight sales metrics dashboard in chat: the user asks about revenue, pipeline, quota, win rate, activity volume, health score, churn risk, or related numeric trends, and the agent responds with text plus optional AG UI rich cards or Vega-Lite charts.

## Core Decisions

- Use one `@graph_fn` as the only agent ingress.
- Use `context.llm()` with the `"default"` profile for all reasoning and tool-call generation.
- Do not use deterministic keyword detection, regex routing, or hard-coded intent detection for generating tool calls.
- Give the LLM general JSON tool schemas as prompt context, not strict provider-specific response schemas, so non-OpenAI APIs remain compatible.
- Use `context.channel("ui:session")` for output.
- Do not use `send_phase`; keep the UI clean.
- Do not use any `ask_*` channel method. The demo is turn-based, and clarification questions must be emitted through `finish`.
- Do not use AetherGraph memory for now. The loop receives explicit chat history and current-turn tool results.
- Keep the data mostly numeric, with only minimal labels for grouping.

## Proposed File Structure

```text
others/crm-dashboard-demo/
  PLAN.md
  src/
    __init__.py
    agent.py
    prompts/
      system.md
      tool_policy.md
    data/
      schema.sql
      seed.py
    db/
      connection.py
      repository.py
    react/
      context.py
      loop.py
      policy.py
      types.py
    tools/
      handler.py
      schemas.py
      validation.py
    ui/
      cards.py
      charts.py
      rich.py
  run_demo.py
```

## Data Schema

Use SQLite with small deterministic seed data. The main query target should be a single enriched view so the LLM does not need complicated joins.

```sql
CREATE TABLE reps (
  rep_id INTEGER PRIMARY KEY,
  rep_name TEXT NOT NULL,
  team TEXT NOT NULL
);

CREATE TABLE accounts (
  account_id INTEGER PRIMARY KEY,
  account_name TEXT NOT NULL,
  segment TEXT NOT NULL,
  region TEXT NOT NULL
);

CREATE TABLE sales_metrics (
  metric_id INTEGER PRIMARY KEY,
  month TEXT NOT NULL,
  account_id INTEGER NOT NULL,
  rep_id INTEGER NOT NULL,

  pipeline_amount REAL NOT NULL,
  closed_won_amount REAL NOT NULL,
  closed_lost_amount REAL NOT NULL,
  forecast_amount REAL NOT NULL,
  quota_amount REAL NOT NULL,

  meetings_count INTEGER NOT NULL,
  calls_count INTEGER NOT NULL,
  emails_count INTEGER NOT NULL,

  opportunities_created INTEGER NOT NULL,
  opportunities_won INTEGER NOT NULL,
  opportunities_lost INTEGER NOT NULL,

  avg_deal_size REAL NOT NULL,
  win_rate REAL NOT NULL,
  discount_rate REAL NOT NULL,
  sales_cycle_days REAL NOT NULL,

  customer_health_score REAL NOT NULL,
  expansion_score REAL NOT NULL,
  churn_risk_score REAL NOT NULL,

  FOREIGN KEY (account_id) REFERENCES accounts(account_id),
  FOREIGN KEY (rep_id) REFERENCES reps(rep_id)
);

CREATE VIEW sales_metrics_enriched AS
SELECT
  sm.*,
  a.account_name,
  a.segment,
  a.region,
  r.rep_name,
  r.team,
  (sm.closed_won_amount - sm.closed_lost_amount) AS net_closed_amount,
  (sm.closed_won_amount / NULLIF(sm.quota_amount, 0)) AS quota_attainment
FROM sales_metrics sm
JOIN accounts a ON a.account_id = sm.account_id
JOIN reps r ON r.rep_id = sm.rep_id;
```

Seed data target:

- 6 to 8 reps
- 12 to 20 accounts
- 6 to 12 months of metrics
- Enough variance for trend, ranking, grouping, and risk questions

## Agent Entrypoint

The initial implementation should expose one graph function:

```python
@graph_fn(
    name="crm_dashboard_agent",
    inputs=["message", "chat_history", "session_id", "user_meta"],
    outputs=["reply"],
    as_agent={
        "id": "crm_dashboard_agent",
        "title": "CRM Dashboard",
        "short_description": "Answers questions about demo sales metrics.",
        "session_kind": "chat",
        "mode": "chat_v1",
    },
)
async def crm_dashboard_agent(
    message: str,
    chat_history: list[dict] | None = None,
    session_id: str | None = None,
    user_meta: dict | None = None,
    *,
    context: NodeContext,
) -> dict:
    ...
```

## Tool Model

The ReAct loop has exactly two tools.

### `query`

Runs a validated read-only SQL query against the demo database.

```json
{
  "tool": "query",
  "args": {
    "sql": "SELECT month, SUM(closed_won_amount) AS revenue FROM sales_metrics_enriched GROUP BY month ORDER BY month",
    "purpose": "Find monthly closed-won revenue trend.",
    "expected_shape": "time_series"
  }
}
```

### `finish`

Ends the turn. It sends text only when `card` is missing or null, otherwise it sends rich UI via `send_rich(text=..., rich=card)`.

```json
{
  "tool": "finish",
  "args": {
    "text": "Closed-won revenue increased month over month, with March showing the strongest result.",
    "card": null
  }
}
```

Rich card example:

```json
{
  "tool": "finish",
  "args": {
    "text": "Here is the current pipeline summary.",
    "card": {
      "kind": "component",
      "payload": {
        "component_type": "ag.ui.card.v1",
        "props": {
          "version": "card.v1",
          "header": {
            "title": "Pipeline Summary",
            "right_text": "Current Quarter",
            "tone": "info"
          },
          "sections": [
            {
              "type": "kv",
              "columns": 2,
              "items": [
                {"label": "Total Pipeline", "value": "$4.2M"},
                {"label": "Forecast", "value": "$2.8M"}
              ]
            }
          ]
        }
      }
    }
  }
}
```

Vega-Lite example:

```json
{
  "tool": "finish",
  "args": {
    "text": "Closed-won revenue by month is shown below.",
    "card": {
      "kind": "plot",
      "title": "Monthly Closed-Won Revenue",
      "payload": {
        "engine": "vega-lite",
        "spec": {
          "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
          "data": {
            "values": [
              {"month": "2026-01", "revenue": 420000},
              {"month": "2026-02", "revenue": 510000}
            ]
          },
          "mark": "bar",
          "encoding": {
            "x": {"field": "month", "type": "ordinal"},
            "y": {"field": "revenue", "type": "quantitative"}
          }
        }
      }
    }
  }
}
```

## ToolResult Contract

Every tool handler returns a visible result back into the ReAct context. Bad calls are not fatal unless the policy layer stops the loop.

```json
{
  "tool": "query",
  "ok": true,
  "error_code": null,
  "error": null,
  "args": {
    "sql": "SELECT month, SUM(closed_won_amount) AS revenue FROM sales_metrics_enriched GROUP BY month ORDER BY month"
  },
  "result": {
    "columns": ["month", "revenue"],
    "rows": [
      {"month": "2026-01", "revenue": 420000}
    ],
    "row_count": 1
  },
  "hint": "Use finish when you have enough data, or run another query for comparison."
}
```

Invalid calls should also become ToolResults:

```json
{
  "tool": "query",
  "ok": false,
  "error_code": "unsafe_sql",
  "error": "Only read-only SELECT queries against sales_metrics_enriched are allowed.",
  "args": {
    "sql": "DELETE FROM sales_metrics"
  },
  "result": null,
  "hint": "Rewrite the request as a SELECT against sales_metrics_enriched."
}
```

Suggested error codes:

- `invalid_json`
- `unknown_tool`
- `invalid_args`
- `unsafe_sql`
- `unknown_column`
- `query_failed`
- `too_many_rows`
- `empty_result`
- `invalid_card_schema`
- `policy_stop`

## SQL Guardrails

The first implementation can use a simple validation layer:

- Allow only one SQL statement.
- Require `SELECT`.
- Allow only `sales_metrics_enriched` as the query surface.
- Reject write/admin keywords such as `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `PRAGMA`, `ATTACH`, and `DETACH`.
- Apply a default `LIMIT 100` when no limit is present.
- Prefer rejecting `SELECT *` so answers stay compact.
- Return validation failures as ToolResults, then let the LLM recover.

The SQL guardrail may inspect SQL for safety. This is not tool-call generation; tool-call generation must remain LLM-driven through `context.llm()`.

## Loop Policy

Use a tiny deterministic policy wrapper around the LLM-driven loop.

- `MAX_REACT_CYCLES = 5`
- If the same canonical `{tool, args}` appears 3 times, stop the loop.
- If max cycles are reached without `finish`, stop the loop.
- Policy stops send predefined text directly through `context.channel("ui:session").send_text(...)`.
- Do not ask the LLM to explain policy stops.

Repeated-call stop message:

```text
I got stuck repeating the same data request, so I stopped this turn instead of looping. Try rephrasing the question or narrowing the metric/time range.
```

Max-cycle stop message:

```text
I could not complete the analysis within the tool-call limit for this turn. Try asking for one metric, time range, or grouping at a time.
```

## Context Composition

Create a centralized context method:

```python
def compose_react_messages(
    *,
    system_prompt: str,
    schema_summary: str,
    tool_schema_summary: str,
    chat_history: list[dict],
    user_message: str,
    tool_results: list[ToolResult],
) -> list[dict[str, str]]:
    ...
```

Implementation comment should be explicit:

```python
# ReAct context includes:
# - immutable system/tool policy
# - compact database schema and allowed query surface
# - general JSON schemas for query and finish tool calls
# - visible chat history provided to this graph_fn call
# - latest user message
# - all tool results produced during this turn
#
# It intentionally excludes persistent memory, hidden channel state,
# deterministic intent routing, regex/keyword tool selection, and direct UI handles.
```

Tool results should be compacted before re-prompting the LLM:

- Keep all current-turn ToolResults.
- Truncate rows to a small limit, such as 25 rows.
- Truncate serialized tool context to a reasonable character budget.

## Prompt Policy

The system prompt should include:

```text
You are a sales metrics dashboard analyst.

You can answer questions only about the demo sales metrics database and the visible chat/tool history.

If the user asks for anything outside this scope, call finish directly with a brief explanation.
If you need clarification, call finish directly with the question you want to ask.
Never call ask_text, ask_approval, ask_file, or any ask_* method.
This is turn-based: the user's future reply will arrive as a new message with chat history.
Never claim facts about the database unless they came from a successful query result.
Use query when you need database facts.
Use finish when you can answer, need clarification, or the request is out of scope.
Return exactly one JSON tool call object and no extra text.
```

The prompt should describe available tools generally, but should not rely on provider-specific strict tool calling. The LLM should produce plain JSON text, and the local handler validates it.

## Implementation Phases

### Phase 1: Skeleton

Status: Completed.

- Create package structure.
- Add `@graph_fn` agent entrypoint.
- Add prompt files.
- Add placeholder loop that calls `context.llm()` and validates JSON.
- Add simple `finish` handler with `send_text` or `send_rich`.

### Phase 2: Data

Status: Completed.

- Add SQLite schema.
- Add deterministic seed generator.
- Add connection helper and repository query function.
- Add schema summary used by the prompt.

### Phase 3: Query Tool

Status: Completed.

- Implement query ToolResult.
- Add SQL guardrails.
- Add row and payload truncation.
- Add useful validation errors and hints.

### Phase 4: ReAct Loop

Status: Completed.

- Implement centralized context composition.
- Attach chat history and current-turn tool results.
- Add max-cycle and repeated-call policy stops.
- Ensure invalid calls become ToolResults and the loop continues.

### Phase 5: Rich UI

Status: Completed.

- Add card helper for KPI summaries.
- Add Vega-Lite helper for simple bar and line charts.
- Validate `finish.card` lightly; if invalid, send text only and record an `invalid_card_schema` ToolResult.

### Phase 6: Demo Smoke

Status: Completed.

- Run local graph with representative questions.
- Confirm text-only finish.
- Confirm query then finish.
- Confirm out-of-scope finish.
- Confirm clarification through finish.
- Confirm repeated-call and max-cycle policy messages.
- Confirm AG UI renders `send_rich` cards and Vega-Lite plots.
