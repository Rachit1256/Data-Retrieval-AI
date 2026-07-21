"""
table_registry.py

Central registry for every table the app knows about: one entry per
detected subtable, across every uploaded file (xlsx sheet, csv, or pdf
page). This is what gives "dynamic access" to spreadsheet data -- each
subtable is its own addressable, independently queryable pandas DataFrame,
instead of one giant blob per file.

Backed by in-memory dicts on `state` (state.files, state.tables) so it
behaves exactly like the rest of this app's storage today. Swap the
internals for a real DB later without touching callers.
"""

import uuid
from datetime import datetime

import state


def register_file(filename, file_type):
    state.files[filename] = {
        "filename": filename,
        "type": file_type,
        "uploaded_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "table_ids": [],
    }
    return filename


def register_table(filename, table):
    """
    table: dict produced by subtable_detector.detect_subtables(), i.e.
    {"name", "sheet", "dataframe", "rows", "columns", ...}
    """
    table_id = f"{filename}::{table['sheet']}::{table['name']}::{uuid.uuid4().hex[:6]}"

    state.tables[table_id] = {
        "id": table_id,
        "filename": filename,
        "sheet": table["sheet"],
        "name": table["name"],
        "dataframe": table["dataframe"],
        "rows": table["rows"],
        "columns": table["columns"],
    }

    if filename in state.files:
        state.files[filename]["table_ids"].append(table_id)

    return table_id


def get_table(table_id):
    return state.tables.get(table_id)


def get_dataframe(table_id):
    entry = state.tables.get(table_id)
    return entry["dataframe"] if entry else None


def list_tables_for_file(filename):
    if filename not in state.files:
        return []
    return [state.tables[tid] for tid in state.files[filename]["table_ids"] if tid in state.tables]


def list_all_tables():
    return list(state.tables.values())


def list_files():
    return list(state.files.values())


def find_tables_by_name(query):
    """Fuzzy match against table name / sheet / filename."""
    query = query.lower().strip()
    if not query:
        return []

    matches = []
    for table in state.tables.values():
        haystack = f"{table['filename']} {table['sheet']} {table['name']}".lower()
        if query in haystack:
            matches.append(table)

    return matches


def find_tables_with_column(column_name):
    """All tables that contain a column matching `column_name` (case-insensitive)."""
    target = column_name.lower().strip()
    matches = []
    for table in state.tables.values():
        for col in table["columns"]:
            if str(col).lower() == target:
                matches.append(table)
                break
    return matches


def largest_table_for_file(filename):
    """Best-effort 'primary table' for a file -- used to keep the existing
    file-level insights/KPIs/report pipeline working without changes."""
    tables = list_tables_for_file(filename)
    if not tables:
        return None
    return max(tables, key=lambda t: t["rows"])


def remove_file(filename):
    if filename in state.files:
        for tid in state.files[filename]["table_ids"]:
            state.tables.pop(tid, None)
        del state.files[filename]


def clear_all():
    state.tables.clear()
    state.files.clear()
