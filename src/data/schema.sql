DROP VIEW IF EXISTS sales_metrics_enriched;
DROP TABLE IF EXISTS sales_metrics;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS reps;

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
