"""
data_tools.py

Plain Python functions with type hints + docstrings. These get handed to
Gemini as callable tools (google-genai's automatic function calling turns
a type-hinted docstringed function straight into a tool schema). Gemini
decides which ones to call and with what arguments; the SDK executes them
in-process and feeds the results back to the model automatically.

Nothing here trusts free-form code from the model -- every function has a
narrow, fixed signature and only ever touches data through
services.table_registry, so "the LLM can call tools" never turns into
"the LLM can run arbitrary code."

Chart-producing tools additionally record what they made into a
thread-local list so the calling route can attach the actual image
filenames to its HTTP response (the model only ever gets to see/describe
the resulting text, not raw bytes).
"""

import threading
import pandas as pd

from services import table_registry
from services import chart_service
from services.rag_service import search as rag_search

_local = threading.local()

AGG_OPS = {"sum", "mean", "max", "min", "count", "median", "std"}
FILTER_OPS = {"==", "!=", ">", "<", ">=", "<=", "contains"}
CHART_TYPES = {"bar", "pie", "line", "scatter", "histogram"}


def reset_capture():
    _local.charts = []


def get_captured_charts():
    return list(getattr(_local, "charts", []))


def _capture(filename, chart_type, title):
    if not hasattr(_local, "charts"):
        _local.charts = []
    _local.charts.append({"image": filename, "type": chart_type, "title": title})


def _get_df(table_id):
    table = table_registry.get_table(table_id)
    if table is None:
        return None, None
    return table, table["dataframe"]


# ---------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------

def list_tables() -> list[dict]:
    """List every table currently available to query. Each uploaded file
    (Excel, CSV, or PDF) may contain several tables -- one per detected
    sheet/subtable. ALWAYS call this first if you don't already know a
    table_id, and whenever the user refers to 'the file' or 'the data'
    without naming a specific table. Returns table_id, filename, sheet,
    table name, row count, and column names for every table."""

    return [
        {
            "table_id": t["id"],
            "filename": t["filename"],
            "sheet": t["sheet"],
            "table_name": t["name"],
            "rows": t["rows"],
            "columns": [str(c) for c in t["columns"]],
        }
        for t in table_registry.list_all_tables()
    ]


def get_table_preview(table_id: str, limit: int = 5) -> dict:
    """Get exact column names, their data types, and a small sample of
    rows from one table. Call this before aggregating or filtering if you
    are not 100% sure of the exact column name or value formatting (e.g.
    'Salary' vs 'salary', or how dates are written)."""

    table, df = _get_df(table_id)
    if df is None:
        return {"error": f"No table with id '{table_id}'. Call list_tables() to see valid ids."}

    return {
        "table_name": table["name"],
        "columns": {str(c): str(df[c].dtype) for c in df.columns},
        "row_count": len(df),
        "sample_rows": df.head(limit).to_dict("records"),
    }


# ---------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------

def aggregate(table_id: str, column: str, operation: str) -> dict:
    """Compute a single number from one column of one table. operation
    must be one of: sum, mean, max, min, count, median, std. Use this for
    questions like 'total revenue', 'average salary', 'highest score'."""

    table, df = _get_df(table_id)
    if df is None:
        return {"error": f"No table with id '{table_id}'."}
    if column not in df.columns:
        return {"error": f"Column '{column}' not found in '{table['name']}'. Columns: {list(df.columns)}"}
    if operation not in AGG_OPS:
        return {"error": f"operation must be one of {sorted(AGG_OPS)}"}

    series = df[column] if operation == "count" else pd.to_numeric(df[column], errors="coerce")

    try:
        value = getattr(series, operation)()
    except Exception as exc:
        return {"error": str(exc)}

    if pd.isna(value):
        return {"error": f"Column '{column}' has no usable numeric values for {operation}()."}

    return {"table": table["name"], "column": column, "operation": operation, "value": float(value) if hasattr(value, "item") else value}


def group_aggregate(table_id: str, group_by: str, value_column: str, operation: str = "sum", top_n: int = 15) -> dict:
    """Group a table by one column and aggregate another column within
    each group. Use this for 'sales by region', 'average salary by
    department', 'count of orders per customer', etc. operation: sum,
    mean, max, min, or count. Returns up to top_n groups, largest first."""

    table, df = _get_df(table_id)
    if df is None:
        return {"error": f"No table with id '{table_id}'."}
    for col in (group_by, value_column):
        if col not in df.columns:
            return {"error": f"Column '{col}' not found in '{table['name']}'. Columns: {list(df.columns)}"}
    if operation not in AGG_OPS - {"std", "median"}:
        return {"error": f"operation must be one of sum, mean, max, min, count"}

    series = pd.to_numeric(df[value_column], errors="coerce") if operation != "count" else df[value_column]

    try:
        grouped = series.groupby(df[group_by]).agg(operation).sort_values(ascending=False).head(top_n)
    except Exception as exc:
        return {"error": str(exc)}

    return {
        "table": table["name"],
        "group_by": group_by,
        "value_column": value_column,
        "operation": operation,
        "groups": [{"group": str(k), "value": (float(v) if hasattr(v, "item") else v)} for k, v in grouped.items()],
    }


def compare_tables(table_ids: list[str], column: str, operation: str = "sum") -> dict:
    """Compare the same aggregation of the same column across two or more
    tables. Use this when the user explicitly wants to compare two
    sheets/tables/time-periods against each other, e.g. 'compare Q1 and
    Q2 revenue' where Q1 and Q2 are two different tables."""

    if operation not in AGG_OPS:
        return {"error": f"operation must be one of {sorted(AGG_OPS)}"}

    results = []
    for table_id in table_ids:
        table, df = _get_df(table_id)
        if df is None or column not in df.columns:
            continue

        series = df[column] if operation == "count" else pd.to_numeric(df[column], errors="coerce")

        try:
            value = getattr(series, operation)()
        except Exception:
            continue

        if pd.isna(value):
            continue

        results.append({"table": table["name"], "value": float(value) if hasattr(value, "item") else value})

    if not results:
        return {"error": f"Could not compute '{operation}' of '{column}' on any of the given tables."}

    return {"column": column, "operation": operation, "results": results}


def filter_rows(table_id: str, column: str, operator: str, value: str, limit: int = 50) -> dict:
    """Return rows from a table matching a condition -- use this for
    'which employees earn more than 50000', 'orders from California',
    'products where category equals Electronics', etc. operator must be
    one of: ==, !=, >, <, >=, <=, contains (case-insensitive substring
    match, for text). Numeric operators coerce the column to numbers
    automatically."""

    table, df = _get_df(table_id)
    if df is None:
        return {"error": f"No table with id '{table_id}'."}
    if column not in df.columns:
        return {"error": f"Column '{column}' not found in '{table['name']}'. Columns: {list(df.columns)}"}
    if operator not in FILTER_OPS:
        return {"error": f"operator must be one of {sorted(FILTER_OPS)}"}

    series = df[column]

    try:
        if operator == "==":
            result = df[series.astype(str).str.strip().str.lower() == str(value).strip().lower()]
        elif operator == "!=":
            result = df[series.astype(str).str.strip().str.lower() != str(value).strip().lower()]
        elif operator == "contains":
            result = df[series.astype(str).str.lower().str.contains(str(value).lower(), na=False)]
        else:
            numeric = pd.to_numeric(series, errors="coerce")
            threshold = float(value)
            if operator == ">":
                result = df[numeric > threshold]
            elif operator == "<":
                result = df[numeric < threshold]
            elif operator == ">=":
                result = df[numeric >= threshold]
            else:
                result = df[numeric <= threshold]
    except (ValueError, TypeError) as exc:
        return {"error": str(exc)}

    return {
        "table": table["name"],
        "match_count": len(result),
        "rows": result.head(limit).to_dict("records"),
        "truncated": len(result) > limit,
    }


# ---------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------

def create_chart(table_id: str, chart_type: str, x_column: str, y_column: str = "", operation: str = "sum", title: str = "") -> dict:
    """Create and save a chart image from one table. ALWAYS call this
    (don't just describe a chart in words) whenever the user asks to
    'plot', 'chart', 'graph', or 'visualize' something. chart_type must
    be one of: bar, pie, line, scatter, histogram.
    - bar/pie: x_column is the category to group by; y_column (optional)
      is a numeric column to aggregate with `operation` (sum/mean/count/
      max/min) -- omit y_column to just count occurrences of x_column.
    - line: x_column is usually a date/sequence column, y_column is the
      numeric value to trend, aggregated with `operation`.
    - scatter: x_column and y_column are both numeric.
    - histogram: x_column is the numeric column to bucket; y_column is
      ignored."""

    table, df = _get_df(table_id)
    if df is None:
        return {"error": f"No table with id '{table_id}'."}
    if chart_type not in CHART_TYPES:
        return {"error": f"chart_type must be one of {sorted(CHART_TYPES)}"}
    if x_column not in df.columns:
        return {"error": f"Column '{x_column}' not found in '{table['name']}'. Columns: {list(df.columns)}"}
    if y_column and y_column not in df.columns:
        return {"error": f"Column '{y_column}' not found in '{table['name']}'. Columns: {list(df.columns)}"}

    chart_title = title or None

    try:
        if chart_type == "bar":
            filename = chart_service.create_bar_chart(df, x_column, y_column or None, operation, chart_title)
        elif chart_type == "pie":
            filename = chart_service.create_pie_chart(df, x_column, y_column or None, operation, chart_title)
        elif chart_type == "line":
            if not y_column:
                return {"error": "line charts need a y_column."}
            filename = chart_service.create_line_chart(df, x_column, y_column, operation, chart_title)
        elif chart_type == "scatter":
            if not y_column:
                return {"error": "scatter charts need a y_column."}
            filename = chart_service.create_scatter_chart(df, x_column, y_column, chart_title)
        else:
            filename = chart_service.create_histogram(df, x_column, title=chart_title)
    except Exception as exc:
        return {"error": f"Could not build chart: {exc}"}

    final_title = chart_title or f"{chart_type} chart of {x_column}" + (f" vs {y_column}" if y_column else "")
    _capture(filename, chart_type, final_title)

    return {"image": filename, "type": chart_type, "title": final_title, "table": table["name"]}


def build_dashboard(table_id: str) -> dict:
    """Build a small dashboard for one table in a single call: a handful
    of key numeric stats plus 2-4 relevant charts, chosen automatically
    based on the table's column types. Use this whenever the user asks
    to 'build a dashboard', 'give me an overview', or 'summarize this
    data visually'."""

    table, df = _get_df(table_id)
    if df is None:
        return {"error": f"No table with id '{table_id}'."}

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        for c in df.columns:
            converted = pd.to_numeric(df[c], errors="coerce")
            if converted.notna().sum() >= max(1, int(0.6 * len(df))):
                numeric_cols.append(c)

    categorical_cols = [c for c in df.columns if c not in numeric_cols][:5]

    kpis = []
    for col in numeric_cols[:5]:
        series = pd.to_numeric(df[col], errors="coerce")
        if series.notna().sum() == 0:
            continue
        kpis.append({
            "column": col,
            "sum": float(series.sum()),
            "mean": round(float(series.mean()), 2),
            "max": float(series.max()),
            "min": float(series.min()),
        })

    charts = []

    if categorical_cols and numeric_cols:
        cat, num = categorical_cols[0], numeric_cols[0]
        try:
            filename = chart_service.create_bar_chart(df, cat, num, "sum", f"Total {num} by {cat}")
            _capture(filename, "bar", f"Total {num} by {cat}")
            charts.append({"image": filename, "type": "bar", "title": f"Total {num} by {cat}"})
        except Exception:
            pass

        try:
            filename = chart_service.create_pie_chart(df, cat, num, "sum", f"{num} distribution by {cat}")
            _capture(filename, "pie", f"{num} distribution by {cat}")
            charts.append({"image": filename, "type": "pie", "title": f"{num} distribution by {cat}"})
        except Exception:
            pass

    if len(numeric_cols) >= 1:
        try:
            filename = chart_service.create_histogram(df, numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
            _capture(filename, "histogram", f"Distribution of {numeric_cols[0]}")
            charts.append({"image": filename, "type": "histogram", "title": f"Distribution of {numeric_cols[0]}"})
        except Exception:
            pass

    if not categorical_cols and len(numeric_cols) < 1:
        # last resort: value counts of the first column
        try:
            filename = chart_service.create_bar_chart(df, df.columns[0], title=f"Counts of {df.columns[0]}")
            _capture(filename, "bar", f"Counts of {df.columns[0]}")
            charts.append({"image": filename, "type": "bar", "title": f"Counts of {df.columns[0]}"})
        except Exception:
            pass

    return {
        "table": table["name"],
        "rows": len(df),
        "columns": list(df.columns),
        "kpis": kpis,
        "charts": charts,
    }


# ---------------------------------------------------------------------
# Narrative fallback
# ---------------------------------------------------------------------

def search_documents(query: str) -> list[str]:
    """Semantic search across every uploaded document (spreadsheets and
    PDFs) for open-ended / narrative questions that don't map to a single
    calculation, e.g. 'what does this PDF say about payment terms'. Only
    use this when list_tables/aggregate/group_aggregate/filter_rows don't
    apply."""

    return rag_search(query, n_results=8)


ALL_TOOLS = [
    list_tables,
    get_table_preview,
    aggregate,
    group_aggregate,
    compare_tables,
    filter_rows,
    create_chart,
    build_dashboard,
    search_documents,
]
