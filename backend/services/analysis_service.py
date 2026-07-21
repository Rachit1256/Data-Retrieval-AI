import pandas as pd


def summarize(df):

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict()
    }


def find_numeric_column(df, question):

    q = question.lower()

    for col in df.columns:
        if col.lower() in q:
            if pd.api.types.is_numeric_dtype(df[col]):
                return col

    return None


def analyze(df, question):

    q = question.lower()

    column = find_numeric_column(df, question)

    if column is None:
        return None

    if "sum" in q or "total" in q:
        return f"Total {column}: {df[column].sum()}"

    if "average" in q or "mean" in q:
        return f"Average {column}: {df[column].mean()}"

    if "max" in q or "highest" in q:
        return f"Highest {column}: {df[column].max()}"

    if "min" in q or "lowest" in q:
        return f"Lowest {column}: {df[column].min()}"

    if "count" in q:
        return f"Count: {df[column].count()}"

    return None