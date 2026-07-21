from datetime import datetime


def build_report(document):

    report = {}

    report["generated_at"] = datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )

    report["rows"] = document["rows"]

    report["columns"] = document["columns"]

    report["insights"] = document["business_insights"]

    report["kpis"] = document["kpis"]

    report["statistics"] = document["insights"]["statistics"]

    return report