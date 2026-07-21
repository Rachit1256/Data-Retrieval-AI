import pandas as pd


def generate_chart_data(df: pd.DataFrame):

    charts = []

    numeric = list(df.select_dtypes(include="number").columns)
    categorical = list(df.select_dtypes(include="object").columns)
    dates = list(df.select_dtypes(include=["datetime64"]).columns)

    # -----------------------------
    # BAR CHARTS
    # -----------------------------
    if categorical:

        category = categorical[0]

        for num in numeric:

            grouped = (
                df.groupby(category)[num]
                .sum()
                .reset_index()
            )

            charts.append({

                "type": "bar",

                "title": f"{num} by {category}",

                "category": category,

                "value": num,

                "data": grouped.to_dict("records")

            })

    # -----------------------------
    # PIE CHART
    # -----------------------------
    if categorical and numeric:

        grouped = (
            df.groupby(categorical[0])[numeric[0]]
            .sum()
            .reset_index()
        )

        charts.append({

            "type": "pie",

            "title": f"{numeric[0]} Distribution",

            "category": categorical[0],

            "value": numeric[0],

            "data": grouped.to_dict("records")

        })

    # -----------------------------
    # LINE CHART
    # -----------------------------
    if dates and numeric:

        grouped = (
            df.groupby(dates[0])[numeric[0]]
            .sum()
            .reset_index()
        )

        charts.append({

            "type": "line",

            "title": f"{numeric[0]} Trend",

            "category": dates[0],

            "value": numeric[0],

            "data": grouped.to_dict("records")

        })

    return charts