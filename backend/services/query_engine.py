"""
query_engine.py

A safer, more general replacement for the old keyword-matching
analysis_service/analyst_service combo. Instead of hardcoding column
names like "salary" and "revenue", this asks Gemini to look at the
*actual* schemas of the tables currently registered (see
services/table_registry.py) and decide what operation would answer the
question, as strict JSON. The operation is then executed with plain
pandas -- Gemini never gets to run arbitrary code, it only ever picks
from a small whitelist of safe aggregation/filter operations. This is
what enables real cross-table comparisons ("compare Q1 vs Q2 revenue",
"which sheet has more customers") on top of the dynamic subtable
registry, instead of only ever looking at one dataframe at a time.
"""

import json
import re

import pandas as pd

from ai.gemini import client
from services import table_registry

ALLOWED_OPERATIONS = {"sum", "mean", "max", "min", "count", "median", "std"}

MAX_CANDIDATE_TABLES = 6
MAX_SAMPLE_ROWS = 3


def _score_table(table, question_tokens):
    haystack_tokens = set(
        re.findall(r"[a-z0-9]+", f"{table['name']} {table['sheet']} {' '.join(map(str, table['columns']))}".lower())
    )
    return len(question_tokens & haystack_tokens)


def select_candidate_tables(question, restrict_to_filename=None):
    """Pick the tables most likely to be relevant to `question`, ranked by
    keyword overlap with table/column names. Falls back to "all tables"
    (capped) if nothing scores above zero, so the model still has context
    for vague questions."""

    all_tables = (
        table_registry.list_tables_for_file(restrict_to_filename)
        if restrict_to_filename
        else table_registry.list_all_tables()
    )

    if not all_tables:
        return []

    question_tokens = set(re.findall(r"[a-z0-9]+", question.lower()))

    scored = sorted(all_tables, key=lambda t: _score_table(t, question_tokens), reverse=True)

    top_scoring = [t for t in scored if _score_table(t, question_tokens) > 0]

    candidates = top_scoring if top_scoring else scored

    return candidates[:MAX_CANDIDATE_TABLES]


def _describe_table(table):
    df = table["dataframe"]
    dtypes = {col: str(df[col].dtype) for col in df.columns}
    sample = df.head(MAX_SAMPLE_ROWS).to_dict("records")

    return {
        "table_id": table["id"],
        "name": table["name"],
        "file": table["filename"],
        "sheet": table["sheet"],
        "rows": table["rows"],
        "columns": dtypes,
        "sample_rows": sample,
    }


def _build_prompt(question, tables):
    schema = json.dumps([_describe_table(t) for t in tables], default=str, indent=2)

    return f"""
You are a data query planner for a spreadsheet assistant. You do NOT
answer the question directly. You decide how to compute the answer from
the tables below, then respond with STRICT JSON only (no markdown, no
prose, no code fences).

Available tables (each is an independent pandas DataFrame):
{schema}

User question:
"{question}"

Respond with exactly one JSON object matching ONE of these shapes:

1) Single-table aggregation:
{{"action": "aggregate", "table_id": "<id>", "column": "<col>", "operation": "sum|mean|max|min|count|median|std"}}

2) Compare the same operation/column across multiple tables:
{{"action": "compare", "table_ids": ["<id>", "<id>"], "column": "<col>", "operation": "sum|mean|max|min|count|median|std"}}

3) Filter/retrieve rows matching a simple equality or threshold condition:
{{"action": "filter", "table_id": "<id>", "column": "<col>", "operator": "==|>|<|>=|<=", "value": <value>}}

4) You cannot answer this with a simple operation (open-ended / narrative question):
{{"action": "none"}}

Only ever reference table_id and column values that appear exactly in the
schema above. If the question doesn't clearly map to one of these
operations, use action "none".
"""


def _parse_json_response(text):
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _run_aggregate(table_id, column, operation):
    df = table_registry.get_dataframe(table_id)

    if df is None or column not in df.columns or operation not in ALLOWED_OPERATIONS:
        return None

    series = pd.to_numeric(df[column], errors="coerce") if operation != "count" else df[column]

    try:
        value = getattr(series, operation)()
    except Exception:
        return None

    return value


def _run_filter(table_id, column, operator, value):
    df = table_registry.get_dataframe(table_id)

    if df is None or column not in df.columns:
        return None

    series = df[column]

    try:
        if operator == "==":
            result = df[series.astype(str).str.lower() == str(value).lower()]
        elif operator == ">":
            result = df[pd.to_numeric(series, errors="coerce") > float(value)]
        elif operator == "<":
            result = df[pd.to_numeric(series, errors="coerce") < float(value)]
        elif operator == ">=":
            result = df[pd.to_numeric(series, errors="coerce") >= float(value)]
        elif operator == "<=":
            result = df[pd.to_numeric(series, errors="coerce") <= float(value)]
        else:
            return None
    except (ValueError, TypeError):
        return None

    return result


def ask_data_engine(question, restrict_to_filename=None):
    """
    Main entry point. Returns a plain-text answer, or None if this
    question doesn't map to a supported operation (caller should fall
    back to RAG / plain chat in that case).
    """

    tables = select_candidate_tables(question, restrict_to_filename)

    if not tables:
        return None

    prompt = _build_prompt(question, tables)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    plan = _parse_json_response(response.text)

    if not plan or plan.get("action") in (None, "none"):
        return None

    action = plan["action"]

    if action == "aggregate":
        table = table_registry.get_table(plan.get("table_id"))
        value = _run_aggregate(plan.get("table_id"), plan.get("column"), plan.get("operation"))

        if value is None or table is None:
            return None

        return f"{plan['operation'].title()} of '{plan['column']}' in {table['name']}: {value}"

    if action == "compare":
        rows = []
        for table_id in plan.get("table_ids", []):
            table = table_registry.get_table(table_id)
            value = _run_aggregate(table_id, plan.get("column"), plan.get("operation"))

            if table is not None and value is not None:
                rows.append(f"• {table['name']}: {value}")

        if not rows:
            return None

        header = f"{plan['operation'].title()} of '{plan['column']}' by table:"
        return header + "\n" + "\n".join(rows)

    if action == "filter":
        table = table_registry.get_table(plan.get("table_id"))
        result = _run_filter(
            plan.get("table_id"), plan.get("column"), plan.get("operator"), plan.get("value")
        )

        if result is None or table is None:
            return None

        if result.empty:
            return f"No matching rows found in {table['name']}."

        preview = result.head(50)
        return f"{len(result)} matching row(s) in {table['name']}:\n{preview.to_string(index=False)}"

    return None
