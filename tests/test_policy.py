from crm_dashboard_demo.react.policy import LoopPolicy, REPEATED_CALL_MESSAGE
from crm_dashboard_demo.react.types import ToolCall


def test_repeated_call_policy_normalizes_sql_whitespace_and_case():
    policy = LoopPolicy()
    call_a = ToolCall(
        tool="query",
        args={"sql": "SELECT month FROM sales_metrics_enriched LIMIT 1"},
    )
    call_b = ToolCall(
        tool="query",
        args={"sql": "  select   month   from sales_metrics_enriched limit 1  "},
    )

    assert policy.record_call(call_a) is None
    assert policy.record_call(call_b) is None
    assert policy.record_call(call_a) == REPEATED_CALL_MESSAGE
