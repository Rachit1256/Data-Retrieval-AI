import pandas as pd


def executive_summary(df: pd.DataFrame):

    summary = []

    summary.append(
        f"The dataset contains {len(df)} records."
    )

    numeric = df.select_dtypes(include="number")

    categorical = df.select_dtypes(include="object")

    if len(df.duplicated()):

        duplicates = int(df.duplicated().sum())

        if duplicates == 0:

            summary.append(
                "No duplicate records detected."
            )

        else:

            summary.append(
                f"{duplicates} duplicate rows were found."
            )

    missing = int(df.isna().sum().sum())

    if missing == 0:

        summary.append(
            "No missing values detected."
        )

    else:

        summary.append(
            f"{missing} missing values require attention."
        )

    for column in numeric.columns:

        summary.append(

            f"{column} ranges from "

            f"{numeric[column].min()} "

            f"to "

            f"{numeric[column].max()}."

        )

    if len(categorical.columns):

        column = categorical.columns[0]

        top = (

            df[column]

            .value_counts()

            .idxmax()

        )

        summary.append(

            f"The most common "

            f"{column} "

            f"is "

            f"{top}."

        )

    return summary