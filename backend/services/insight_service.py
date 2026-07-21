import pandas as pd


def generate_insights(df: pd.DataFrame):

    insights = {}

    # ------------------------
    # Dataset Information
    # ------------------------

    insights["rows"] = len(df)

    insights["columns"] = len(df.columns)

    insights["column_names"] = list(df.columns)

    insights["numeric_columns"] = list(
        df.select_dtypes(include="number").columns
    )

    insights["categorical_columns"] = list(
        df.select_dtypes(include="object").columns
    )

    insights["date_columns"] = list(
        df.select_dtypes(include="datetime").columns
    )

    # ------------------------
    # Missing Values
    # ------------------------

    insights["missing_values"] = (
        df.isna()
        .sum()
        .to_dict()
    )

    # ------------------------
    # Duplicate Rows
    # ------------------------

    insights["duplicates"] = int(df.duplicated().sum())

    # ------------------------
    # Memory Usage
    # ------------------------

    insights["memory_usage"] = round(

        df.memory_usage(deep=True).sum() / 1024,

        2

    )

    # ------------------------
    # Numeric Statistics
    # ------------------------

    statistics = {}

    numeric_df = df.select_dtypes(include="number")

    for column in numeric_df.columns:

        statistics[column] = {

            "average": float(numeric_df[column].mean()),

            "minimum": float(numeric_df[column].min()),

            "maximum": float(numeric_df[column].max()),

            "median": float(numeric_df[column].median()),

            "sum": float(numeric_df[column].sum())

        }

    insights["statistics"] = statistics

    return insights