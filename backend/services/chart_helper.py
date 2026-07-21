def detect_chart_column(df, question):

    q = question.lower()

    for col in df.columns:

        if col.lower() in q:

            return col

    return None