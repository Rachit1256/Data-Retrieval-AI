import pandas as pd


def generate_business_insights(df: pd.DataFrame):

    insights = []

    # Dataset Size
    insights.append(
        f"Dataset contains {len(df)} rows and {len(df.columns)} columns."
    )

    # Duplicate Rows
    duplicates = df.duplicated().sum()

    if duplicates == 0:
        insights.append("No duplicate rows detected.")
    else:
        insights.append(
            f"{duplicates} duplicate rows were found."
        )

    # Missing Values
    missing = df.isna().sum()

    for column, value in missing.items():

        if value == 0:
            continue

        insights.append(
            f"{column} contains {value} missing values."
        )

    # Numeric Columns
    numeric = df.select_dtypes(include="number")

    for column in numeric.columns:

        insights.append(

            f"{column}: Average = {round(numeric[column].mean(),2)}, "
            f"Minimum = {numeric[column].min()}, "
            f"Maximum = {numeric[column].max()}"

        )

    return insights