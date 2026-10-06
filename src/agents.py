from __future__ import annotations

import os
from typing import Any, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from .tools import run_sql_tool, schema, validate_result

load_dotenv()

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None


class AnalystState(TypedDict, total=False):
    question: str
    intent: str
    sql: str
    result: dict[str, Any]
    validation_issues: list[str]
    analysis: str
    answer: str
    route: str


def orchestrator(state: AnalystState) -> AnalystState:
    q = state["question"].lower()
    data_words = ("revenue", "sales", "orders", "customers", "region", "product", "category", "top", "average", "monthly")
    intent = "data_analysis" if any(w in q for w in data_words) else "unsupported"
    return {"intent": intent, "route": "data_agent" if intent == "data_analysis" else "response_agent"}


def _deterministic_sql(question: str) -> str:
    q = question.lower()
    if "monthly" in q or "month" in q:
        return "SELECT substr(order_date,1,7) AS month, ROUND(SUM(revenue),2) AS revenue FROM sales GROUP BY month ORDER BY month"
    if "region" in q:
        return "SELECT region, ROUND(SUM(revenue),2) AS revenue, COUNT(*) AS orders FROM sales GROUP BY region ORDER BY revenue DESC"
    if "category" in q:
        return "SELECT category, ROUND(SUM(revenue),2) AS revenue, SUM(quantity) AS units FROM sales GROUP BY category ORDER BY revenue DESC"
    if "product" in q or "top" in q:
        return "SELECT product, ROUND(SUM(revenue),2) AS revenue, SUM(quantity) AS units FROM sales GROUP BY product ORDER BY revenue DESC LIMIT 10"
    if "customer" in q:
        return "SELECT c.customer_name, c.segment, ROUND(SUM(s.revenue),2) AS revenue FROM sales s JOIN customers c ON s.customer_id=c.customer_id GROUP BY c.customer_id ORDER BY revenue DESC"
    if "average" in q:
        return "SELECT ROUND(AVG(revenue),2) AS average_order_revenue, COUNT(*) AS orders FROM sales"
    return "SELECT ROUND(SUM(revenue),2) AS total_revenue, COUNT(*) AS orders, ROUND(AVG(revenue),2) AS average_order_revenue FROM sales"


def _llm_sql(question: str) -> str | None:
    if not (ChatOpenAI and os.getenv("OPENAI_API_KEY")):
        return None
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    prompt = f"""Convert the user's analytics question into one safe SQLite SELECT query.\nSchema: {schema()}\nRules: SELECT/WITH only; no writes; use exact column names; return SQL only.\nQuestion: {question}"""
    response = model.invoke(prompt)
    sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    if sql.upper().startswith(("SELECT", "WITH")):
        return sql
    return None


def data_agent(state: AnalystState) -> AnalystState:
    sql = _llm_sql(state["question"]) or _deterministic_sql(state["question"])
    return {"sql": sql}


def sql_agent(state: AnalystState) -> AnalystState:
    return {"result": run_sql_tool(state["sql"])}


def validation_agent(state: AnalystState) -> AnalystState:
    return {"validation_issues": validate_result(state["result"])}


def analytics_agent(state: AnalystState) -> AnalystState:
    rows = state.get("result", {}).get("rows", [])
    if not rows:
        return {"analysis": "No data was returned."}
    if len(rows) == 1:
        return {"analysis": f"The query returned {rows[0]}"}
    first = rows[0]
    numeric = [v for v in first.values() if isinstance(v, (int, float))]
    return {"analysis": f"Returned {len(rows)} rows. Highest-ranked result: {first}. Numeric values in the first result: {numeric}."}


def response_agent(state: AnalystState) -> AnalystState:
    if state.get("intent") == "unsupported":
        return {"answer": "I can answer questions about the sample sales and customer data, such as revenue, orders, customers, products, categories, regions, and monthly trends."}
    if state.get("validation_issues"):
        return {"answer": "I could not produce a validated answer: " + "; ".join(state["validation_issues"])}
    return {"answer": f"{state.get('analysis', 'No analysis available.')}\n\nSQL used:\n{state.get('sql', '')}"}


def _route(state: AnalystState) -> str:
    return state.get("route", "response_agent")


def build_graph():
    graph = StateGraph(AnalystState)
    graph.add_node("orchestrator", orchestrator)
    graph.add_node("data_agent", data_agent)
    graph.add_node("sql_agent", sql_agent)
    graph.add_node("validation_agent", validation_agent)
    graph.add_node("analytics_agent", analytics_agent)
    graph.add_node("response_agent", response_agent)
    graph.set_entry_point("orchestrator")
    graph.add_conditional_edges("orchestrator", _route, {"data_agent": "data_agent", "response_agent": "response_agent"})
    graph.add_edge("data_agent", "sql_agent")
    graph.add_edge("sql_agent", "validation_agent")
    graph.add_edge("validation_agent", "analytics_agent")
    graph.add_edge("analytics_agent", "response_agent")
    graph.add_edge("response_agent", END)
    return graph.compile()


def ask(question: str) -> AnalystState:
    return build_graph().invoke({"question": question})
