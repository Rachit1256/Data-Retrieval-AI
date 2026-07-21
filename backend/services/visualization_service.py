import pandas as pd


def detect_visualizations(df: pd.DataFrame):

    charts = []

    numeric = list(df.select_dtypes(include="number").columns)

    categorical = list(df.select_dtypes(include="object").columns)

    dates = list(df.select_dtypes(include=["datetime64"]).columns)

    # -----------------------
    # Bar Charts
    # -----------------------

    if categorical and numeric:

        category = categorical[0]

        for num in numeric:

            charts.append({

                "type": "bar",

                "title": f"{num} by {category}",

                "x": category,

                "y": num

            })

    # -----------------------
    # Line Charts
    # -----------------------

    if dates and numeric:

        date = dates[0]

        for num in numeric:

            charts.append({

                "type": "line",

                "title": f"{num} over Time",

                "x": date,

                "y": num

            })

    # -----------------------
    # Pie Charts
    # -----------------------

    if categorical:

        charts.append({

            "type": "pie",

            "title": f"{categorical[0]} Distribution",

            "column": categorical[0]

        })

    # -----------------------
    # Histogram
    # -----------------------

    for num in numeric:

        charts.append({

            "type": "histogram",

            "title": f"{num} Distribution",

            "column": num

        })

    # -----------------------
    # Scatter Plot
    # -----------------------

    if len(numeric) >= 2:

        charts.append({

            "type": "scatter",

            "title": f"{numeric[0]} vs {numeric[1]}",

            "x": numeric[0],

            "y": numeric[1]

        })

    return charts