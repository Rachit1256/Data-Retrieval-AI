import pandas as pd


def export_excel(report, filename):

    df = pd.DataFrame(

        report["kpis"]

    )

    df.to_excel(

        filename,

        index=False

    )

    return filename