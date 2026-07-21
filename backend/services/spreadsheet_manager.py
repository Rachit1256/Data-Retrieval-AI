import state


def list_files():
    """
    Return list of uploaded filenames.
    """

    return list(state.documents.keys())


def get_dataframe(filename):
    """
    Return dataframe of a specific spreadsheet.
    """

    if filename not in state.documents:
        return None

    return state.documents[filename]["data"]


def get_metadata(filename):

    if filename not in state.documents:
        return None

    info = state.documents[filename]

    return {
        "rows": info["rows"],
        "columns": info["columns"],
        "uploaded_at": info["uploaded_at"]
    }


def remove_file(filename):

    if filename in state.documents:
        del state.documents[filename]


def clear():

    state.documents.clear()