from __future__ import annotations

import csv
import re
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "analytics.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.executescript("""
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS customers;
        CREATE TABLE sales (
            order_id INTEGER PRIMARY KEY, order_date TEXT, customer_id TEXT,
            region TEXT, product TEXT, category TEXT, quantity INTEGER,
            unit_price REAL, revenue REAL
        );
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY, customer_name TEXT,
            segment TEXT, city TEXT
        );
        """)
        with open(ROOT / "data/sales.csv", newline="", encoding="utf-8") as f:
            rows = [tuple(r.values()) for r in csv.DictReader(f)]
        con.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?)", rows)
        with open(ROOT / "data/customers.csv", newline="", encoding="utf-8") as f:
            rows = [tuple(r.values()) for r in csv.DictReader(f)]
        con.executemany("INSERT INTO customers VALUES (?,?,?,?)", rows)
        con.commit()


def execute_sql(sql: str) -> list[dict[str, Any]]:
    sql = sql.strip().rstrip(";")
    if not re.match(r"^(SELECT|WITH)\b", sql, re.I):
        raise ValueError("Only read-only SELECT/WITH queries are allowed.")
    if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|PRAGMA)\b", sql, re.I):
        raise ValueError("Unsafe SQL detected.")
    if not DB_PATH.exists():
        init_db()
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        return [dict(r) for r in con.execute(sql).fetchall()]


def schema() -> str:
    return "sales(order_id, order_date, customer_id, region, product, category, quantity, unit_price, revenue)\ncustomers(customer_id, customer_name, segment, city)"


def run_sql_tool(sql: str) -> dict[str, Any]:
    rows = execute_sql(sql)
    return {"sql": sql, "row_count": len(rows), "rows": rows}


def validate_result(result: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not result.get("sql"):
        issues.append("No SQL was generated.")
    if result.get("row_count", 0) == 0:
        issues.append("Query returned no rows.")
    for row in result.get("rows", []):
        for value in row.values():
            if isinstance(value, float) and (value != value or abs(value) == float("inf")):
                issues.append("Result contains a non-finite numeric value.")
    return issues
