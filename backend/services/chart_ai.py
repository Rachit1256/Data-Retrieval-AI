def recommend_chart(question):

    q = question.lower()

    if "trend" in q:

        return "line"

    if "distribution" in q:

        return "histogram"

    if "compare" in q:

        return "bar"

    if "relationship" in q:

        return "scatter"

    if "percentage" in q:

        return "pie"

    return "bar"