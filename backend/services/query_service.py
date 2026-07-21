import re
import pandas as pd


def normalize(text):
    return str(text).strip().lower()


def query_dataframe(df, question):

    q = question.lower()

    # -------- Exact value matching --------
    for column in df.columns:

        for value in df[column].astype(str).unique():

            if normalize(value) in q:

                result = df[
                    df[column].astype(str).str.lower() == normalize(value)
                ]

                if not result.empty:
                    return result.to_string(index=False)

    # -------- Numeric comparison --------
    pattern = r"(greater than|above|less than|below)\s+(\d+)"

    match = re.search(pattern, q)

    if match:

        operation = match.group(1)
        number = float(match.group(2))

        for col in df.select_dtypes(include="number").columns:

            if col.lower() in q:

                if operation in ["greater than", "above"]:
                    result = df[df[col] > number]

                else:
                    result = df[df[col] < number]

                return result.to_string(index=False)

    return None