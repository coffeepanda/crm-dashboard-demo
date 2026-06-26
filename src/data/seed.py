from __future__ import annotations

import random
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

REPS = [
    (1, "Avery Chen", "Enterprise"),
    (2, "Maya Patel", "Enterprise"),
    (3, "Jordan Lee", "Commercial"),
    (4, "Sam Rivera", "Commercial"),
    (5, "Taylor Brooks", "Growth"),
    (6, "Riley Morgan", "Growth"),
    (7, "Casey Nguyen", "Strategic"),
    (8, "Drew Kim", "Strategic"),
]

ACCOUNTS = [
    (1, "Acme Robotics", "Enterprise", "West"),
    (2, "Northstar Health", "Enterprise", "East"),
    (3, "Summit Foods", "Commercial", "Central"),
    (4, "Pioneer Bank", "Enterprise", "East"),
    (5, "Atlas Retail", "Commercial", "West"),
    (6, "BluePeak SaaS", "Growth", "West"),
    (7, "Cobalt Energy", "Strategic", "Central"),
    (8, "BrightPath EDU", "Growth", "East"),
    (9, "Harbor Logistics", "Commercial", "South"),
    (10, "Keystone Media", "Growth", "West"),
    (11, "Nova Pharma", "Strategic", "East"),
    (12, "Vector AI", "Enterprise", "West"),
    (13, "Evergreen Insurance", "Commercial", "Central"),
    (14, "Quantum Devices", "Strategic", "West"),
    (15, "Clearwater Telecom", "Enterprise", "South"),
    (16, "MetricWorks", "Growth", "Central"),
]

MONTHS = [
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
    "2026-05",
    "2026-06",
    "2026-07",
    "2026-08",
    "2026-09",
]


def seed_database(db_path: str | Path) -> Path:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)

    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executemany("INSERT INTO reps(rep_id, rep_name, team) VALUES (?, ?, ?)", REPS)
        conn.executemany(
            "INSERT INTO accounts(account_id, account_name, segment, region) VALUES (?, ?, ?, ?)",
            ACCOUNTS,
        )

        metric_id = 1
        rows = []
        for month_index, month in enumerate(MONTHS):
            seasonal = 1.0 + month_index * 0.035
            for account_id, _account_name, segment, region in ACCOUNTS:
                rep_id = ((account_id + month_index) % len(REPS)) + 1
                segment_mult = {
                    "Growth": 0.55,
                    "Commercial": 0.85,
                    "Enterprise": 1.35,
                    "Strategic": 1.75,
                }[segment]
                region_mult = {
                    "West": 1.08,
                    "East": 1.02,
                    "Central": 0.96,
                    "South": 0.9,
                }[region]
                base = 65000 * segment_mult * region_mult * seasonal
                pipeline_amount = round(base * rng.uniform(2.0, 4.8), 2)
                win_rate = round(min(0.82, max(0.18, rng.uniform(0.22, 0.58) + month_index * 0.01)), 3)
                closed_won_amount = round(pipeline_amount * win_rate * rng.uniform(0.18, 0.34), 2)
                closed_lost_amount = round(pipeline_amount * rng.uniform(0.05, 0.18), 2)
                forecast_amount = round(pipeline_amount * rng.uniform(0.38, 0.72), 2)
                quota_amount = round(base * rng.uniform(0.9, 1.45), 2)
                opportunities_created = rng.randint(2, 14)
                opportunities_won = max(0, round(opportunities_created * win_rate * rng.uniform(0.35, 0.75)))
                opportunities_lost = rng.randint(0, max(1, opportunities_created - opportunities_won))
                avg_deal_size = round(
                    closed_won_amount / opportunities_won if opportunities_won else closed_won_amount,
                    2,
                )
                discount_rate = round(rng.uniform(0.03, 0.22), 3)
                sales_cycle_days = round(rng.uniform(24, 95) * (1.15 if segment == "Strategic" else 1.0), 1)
                customer_health_score = round(rng.uniform(48, 95), 1)
                expansion_score = round(rng.uniform(30, 92), 1)
                churn_risk_score = round(max(4, 100 - customer_health_score + rng.uniform(-8, 16)), 1)
                meetings_count = rng.randint(1, 16)
                calls_count = rng.randint(8, 72)
                emails_count = rng.randint(20, 180)

                rows.append(
                    (
                        metric_id,
                        month,
                        account_id,
                        rep_id,
                        pipeline_amount,
                        closed_won_amount,
                        closed_lost_amount,
                        forecast_amount,
                        quota_amount,
                        meetings_count,
                        calls_count,
                        emails_count,
                        opportunities_created,
                        opportunities_won,
                        opportunities_lost,
                        avg_deal_size,
                        win_rate,
                        discount_rate,
                        sales_cycle_days,
                        customer_health_score,
                        expansion_score,
                        churn_risk_score,
                    )
                )
                metric_id += 1

        conn.executemany(
            """
            INSERT INTO sales_metrics(
              metric_id, month, account_id, rep_id,
              pipeline_amount, closed_won_amount, closed_lost_amount, forecast_amount, quota_amount,
              meetings_count, calls_count, emails_count,
              opportunities_created, opportunities_won, opportunities_lost,
              avg_deal_size, win_rate, discount_rate, sales_cycle_days,
              customer_health_score, expansion_score, churn_risk_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()

    return path


if __name__ == "__main__":
    seed_database(Path(__file__).with_name("crm.sqlite"))
