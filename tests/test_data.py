from crm_dashboard_demo.data.seed import seed_database
from crm_dashboard_demo.db.repository import run_select_query


def test_seeded_database_supports_enriched_view(tmp_path):
    db_path = seed_database(tmp_path / "crm.sqlite")

    result = run_select_query(
        "SELECT month, SUM(closed_won_amount) AS revenue "
        "FROM sales_metrics_enriched GROUP BY month ORDER BY month LIMIT 3",
        db_path=db_path,
    )

    assert result["columns"] == ["month", "revenue"]
    assert result["row_count"] == 3
    assert result["rows"][0]["revenue"] > 0
