import state


def resolve_context(question: str):

    q = question.lower()

    if not state.last_column:
        return question

    pronouns = [

        "it",
        "that",
        "this",
        "same",
        "again"

    ]

    for word in pronouns:

        q = q.replace(

            word,

            state.last_column

        )

    return q