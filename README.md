# CRM Dashboard Demo

Backend-only AetherGraph demo agent for asking dashboard-style questions about a small numeric sales metrics database. The agent is implemented as one `@graph_fn` with a simple LLM-driven ReAct loop and two tools: `query` and `finish`.

## Dependencies

Install AetherGraph:

```powershell
pip install aethergraph
```

The demo includes its SQLite seed data at `src/data/crm.sqlite`. If you delete it locally, the app can recreate it from `src/data/seed.py`.

## Start The Agent

From this folder:

```powershell
python run_demo.py
```

The CLI will print the local AG UI URL. Open that URL in your browser.

In the UI, use the left sidebar:

1. Click **Agent**.
2. Select **CRM Dashboard**.
3. Start chatting with the agent.

The default AetherGraph workspace folder, `aethergraph_workspace/`, is runtime output and is ignored by Git.

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
