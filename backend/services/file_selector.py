import state


def detect_file(question: str):

    question = question.lower()

    for filename in state.documents.keys():

        if filename.lower().replace(".xlsx", "") in question:

            return filename

    return None