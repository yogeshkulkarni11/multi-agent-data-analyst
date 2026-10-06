from src.agents import ask
from src.tools import init_db, run_sql_tool, validate_result


def test_sql_tool_reads_sales():
    init_db()
    result = run_sql_tool("SELECT COUNT(*) AS orders FROM sales")
    assert result["rows"][0]["orders"] == 20


def test_multi_agent_revenue_flow():
    state = ask("What is total revenue?")
    assert state["intent"] == "data_analysis"
    assert state["result"]["row_count"] == 1
    assert "total_revenue" in state["result"]["rows"][0]
    assert state["validation_issues"] == []


def test_unsupported_route():
    state = ask("Tell me a joke")
    assert state["intent"] == "unsupported"
    assert "sample sales" in state["answer"]


def test_sql_guardrail():
    try:
        run_sql_tool("DROP TABLE sales")
        assert False, "Unsafe SQL should fail"
    except ValueError:
        assert True


def test_validation_flags_empty_result():
    issues = validate_result({"sql": "SELECT * FROM sales WHERE 1=0", "row_count": 0, "rows": []})
    assert "Query returned no rows." in issues
