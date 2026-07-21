def detect_intent(question: str):

    q = question.lower()

    analysis_words = [
        "sum",
        "total",
        "average",
        "mean",
        "max",
        "highest",
        "minimum",
        "lowest",
        "count",
        "median",
        "statistics"
    ]

    visualization_words = [

    "chart",
    "graph",
    "plot",
    "visualize",
    "pie",
    "bar",
    "histogram",
    "line graph",
    "dashboard"
    ]

    if any(word in q for word in analysis_words):
        return "analysis"

    if any(word in q for word in visualization_words):
        return "visualization"

    return "qa"