from src.tools.validation import validate_select_sql


def test_validate_select_sql_adds_limit():
    result = validate_select_sql(
        "SELECT month, SUM(closed_won_amount) AS revenue "
        "FROM sales_metrics_enriched GROUP BY month ORDER BY month"
    )

    assert result.ok
    assert result.sql.endswith("LIMIT 100")


def test_validate_select_sql_rejects_writes():
    result = validate_select_sql("DELETE FROM sales_metrics_enriched")

    assert not result.ok
    assert result.error_code == "unsafe_sql"


def test_validate_select_sql_rejects_select_star():
    result = validate_select_sql("SELECT * FROM sales_metrics_enriched")

    assert not result.ok
    assert result.error_code == "invalid_args"
