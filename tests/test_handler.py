from crm_dashboard_demo.tools.handler import parse_tool_call


def test_parse_tool_call_valid_query():
    call, error = parse_tool_call(
        '{"tool":"query","args":{"sql":"SELECT month FROM sales_metrics_enriched LIMIT 1"}}'
    )

    assert error is None
    assert call is not None
    assert call.tool == "query"


def test_parse_tool_call_invalid_json_returns_tool_result():
    call, error = parse_tool_call("not json")

    assert call is None
    assert error is not None
    assert error.error_code == "invalid_json"


def test_parse_tool_call_unknown_tool_returns_tool_result():
    call, error = parse_tool_call('{"tool":"chart","args":{}}')

    assert call is None
    assert error is not None
    assert error.error_code == "unknown_tool"
