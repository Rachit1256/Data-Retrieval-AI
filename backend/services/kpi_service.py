import pandas as pd


def detect_kpis(df: pd.DataFrame):

    kpis = []

    columns = {
        c.lower(): c
        for c in df.columns
    }

    # ------------------------
    # Total Rows
    # ------------------------

    kpis.append({

        "title": "Rows",

        "value": len(df)

    })

    # ------------------------
    # Revenue
    # ------------------------

    if "revenue" in columns:

        column = columns["revenue"]

        kpis.append({

            "title": "Revenue",

            "value": round(df[column].sum(), 2)

        })

    # ------------------------
    # Sales
    # ------------------------

    if "sales" in columns:

        column = columns["sales"]

        kpis.append({

            "title": "Sales",

            "value": round(df[column].sum(), 2)

        })

    # ------------------------
    # Profit
    # ------------------------

    if "profit" in columns:

        column = columns["profit"]

        kpis.append({

            "title": "Profit",

            "value": round(df[column].sum(), 2)

        })

    # ------------------------
    # Salary
    # ------------------------

    if "salary" in columns:

        column = columns["salary"]

        kpis.append({

            "title": "Average Salary",

            "value": round(df[column].mean(), 2)

        })

    # ------------------------
    # Quantity
    # ------------------------

    if "quantity" in columns:

        column = columns["quantity"]

        kpis.append({

            "title": "Quantity",

            "value": round(df[column].sum(), 2)

        })

    # ------------------------
    # Age
    # ------------------------

    if "age" in columns:

        column = columns["age"]

        kpis.append({

            "title": "Average Age",

            "value": round(df[column].mean(), 2)

        })

    return kpis