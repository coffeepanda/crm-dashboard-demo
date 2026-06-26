SCHEMA_SUMMARY = """
Allowed query surface: sales_metrics_enriched only.

Columns:
- month TEXT, formatted YYYY-MM
- account_name TEXT
- segment TEXT
- region TEXT
- rep_name TEXT
- team TEXT
- pipeline_amount REAL
- closed_won_amount REAL
- closed_lost_amount REAL
- forecast_amount REAL
- quota_amount REAL
- meetings_count INTEGER
- calls_count INTEGER
- emails_count INTEGER
- opportunities_created INTEGER
- opportunities_won INTEGER
- opportunities_lost INTEGER
- avg_deal_size REAL
- win_rate REAL, 0.0 to 1.0
- discount_rate REAL, 0.0 to 1.0
- sales_cycle_days REAL
- customer_health_score REAL, 0 to 100
- expansion_score REAL, 0 to 100
- churn_risk_score REAL, 0 to 100
- net_closed_amount REAL
- quota_attainment REAL
""".strip()


TOOL_SCHEMA_SUMMARY = """
Return exactly one JSON object and no extra text.

Tool: query
Purpose: read facts from the sales metrics database.
Shape:
{
  "tool": "query",
  "args": {
    "sql": "SELECT ... FROM sales_metrics_enriched ...",
    "purpose": "Short reason for the query.",
    "expected_shape": "table | ranking | time_series | aggregate | comparison"
  }
}

Tool: finish
Purpose: end the turn by sending the user-facing response. Use this for final answers,
out-of-scope requests, and clarification questions.
Shape:
{
  "tool": "finish",
  "args": {
    "text": "User-facing response or question.",
    "card": null
  }
}

If a visual is useful, card may be either a single AG UI block or a blocks wrapper.

Vega-Lite plots must use this exact AG UI block shape:
{
  "kind": "plot",
  "title": "Chart title",
  "payload": {
    "engine": "vega-lite",
    "spec": {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "data": {"values": [{"x": "A", "y": 1}]},
      "mark": "bar",
      "encoding": {
        "x": {"field": "x", "type": "ordinal"},
        "y": {"field": "y", "type": "quantitative"}
      }
    }
  }
}

Generic cards must use kind component with payload.component_type ag.ui.card.v1.
Multiple blocks may use {"blocks": [block, block]}.
""".strip()
