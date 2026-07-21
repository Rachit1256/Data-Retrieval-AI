"""
chart_service.py

All chart-rendering lives here. Every function saves a PNG into charts/
and returns just the filename -- the existing /charts static mount
(see app.py) already serves that directory, so the frontend can show
these with <img src={`${API_BASE}/charts/${filename}`} />.

Kept deliberately dumb: given clean inputs, draw a chart. All the
"what should I chart" decision-making lives in chat_agent.py.
"""

import os
import uuid
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHARTS_DIR = "charts"


def _new_path():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.png"
    return filename, os.path.join(CHARTS_DIR, filename)


def create_bar_chart(df, x_column, y_column=None, agg="sum", title=None):
    """Bar chart. If y_column is given, groups by x_column and aggregates
    y_column (sum/mean/count/max/min). Otherwise falls back to counting
    occurrences of each value in x_column."""

    filename, filepath = _new_path()

    if y_column and y_column in df.columns:
        numeric = pd.to_numeric(df[y_column], errors="coerce")
        grouped = numeric.groupby(df[x_column]).agg(agg).sort_values(ascending=False).head(25)
        ylabel = f"{agg}({y_column})"
    else:
        grouped = df[x_column].value_counts().head(25)
        ylabel = "count"

    plt.figure(figsize=(9, 5))
    grouped.plot(kind="bar", color="#4C72B0")
    plt.title(title or f"{ylabel} by {x_column}")
    plt.xlabel(x_column)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filename


def create_pie_chart(df, column, value_column=None, agg="sum", title=None):
    filename, filepath = _new_path()

    if value_column and value_column in df.columns:
        numeric = pd.to_numeric(df[value_column], errors="coerce")
        grouped = numeric.groupby(df[column]).agg(agg).sort_values(ascending=False).head(12)
    else:
        grouped = df[column].value_counts().head(12)

    plt.figure(figsize=(6, 6))
    grouped.plot(kind="pie", autopct="%1.1f%%")
    plt.ylabel("")
    plt.title(title or f"Distribution of {column}")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filename


def create_line_chart(df, x_column, y_column, agg="sum", title=None):
    filename, filepath = _new_path()

    numeric = pd.to_numeric(df[y_column], errors="coerce")
    data = pd.DataFrame({x_column: df[x_column], y_column: numeric})

    try:
        data[x_column] = pd.to_datetime(data[x_column])
        data = data.sort_values(x_column)
    except (ValueError, TypeError):
        pass

    grouped = data.groupby(x_column)[y_column].agg(agg)

    plt.figure(figsize=(9, 5))
    grouped.plot(kind="line", marker="o", color="#55A868")
    plt.title(title or f"{y_column} trend by {x_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filename


def create_scatter_chart(df, x_column, y_column, title=None):
    filename, filepath = _new_path()

    x = pd.to_numeric(df[x_column], errors="coerce")
    y = pd.to_numeric(df[y_column], errors="coerce")

    plt.figure(figsize=(7, 6))
    plt.scatter(x, y, alpha=0.6, color="#C44E52")
    plt.title(title or f"{y_column} vs {x_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filename


def create_histogram(df, column, bins=20, title=None):
    filename, filepath = _new_path()

    numeric = pd.to_numeric(df[column], errors="coerce").dropna()

    plt.figure(figsize=(8, 5))
    numeric.plot(kind="hist", bins=bins, color="#8172B2")
    plt.title(title or f"Distribution of {column}")
    plt.xlabel(column)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filename
