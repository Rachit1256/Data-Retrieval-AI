"""
subtable_detector.py

Detects one or more logical tables ("subtables") living inside a single
Excel sheet / CSV grid / extracted PDF table.

Real-world spreadsheets often stack several small tables in one sheet,
side by side or one above another, sometimes with a title row above each
header. Pandas' default `read_excel` has no idea any of this is happening
and just reads the sheet as one blob. This module fixes that:

  1. Read the sheet as a *raw* grid (header=None) so nothing is assumed.
  2. Split the grid into blocks separated by fully-blank rows.
  3. Within each block, split into segments separated by fully-blank columns
     (handles tables placed side-by-side).
  4. For each block/segment, detect an optional title row and a header row,
     then build a clean, typed DataFrame out of it.

The output is a list of dicts, each describing one detected table:

    {
        "name": "Employees",              # best-effort table name
        "sheet": "Sheet1",                # source sheet / page / csv
        "dataframe": <pd.DataFrame>,       # cleaned + typed data
        "start_row": 2, "end_row": 40,
        "start_col": 0, "end_col": 5,
        "rows": 38,
        "columns": ["id", "name", "salary"]
    }
"""

import pandas as pd


def _is_blank(value):
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _row_is_blank(row):
    return all(_is_blank(v) for v in row)


def _col_is_blank(raw_df, col_idx, row_start, row_end):
    return all(_is_blank(raw_df.iat[r, col_idx]) for r in range(row_start, row_end + 1))


def _find_row_blocks(raw_df):
    """Split a raw grid into vertical blocks separated by fully-blank rows."""
    n_rows = len(raw_df)
    blocks = []
    start = None

    for r in range(n_rows):
        blank = _row_is_blank(raw_df.iloc[r])

        if not blank and start is None:
            start = r

        if blank and start is not None:
            blocks.append((start, r - 1))
            start = None

    if start is not None:
        blocks.append((start, n_rows - 1))

    return blocks


def _find_col_segments(raw_df, row_start, row_end):
    """Within a row range, split into horizontal segments separated by
    fully-blank columns (handles tables placed side-by-side)."""
    n_cols = raw_df.shape[1]
    segments = []
    start = None

    for c in range(n_cols):
        blank = _col_is_blank(raw_df, c, row_start, row_end)

        if not blank and start is None:
            start = c

        if blank and start is not None:
            segments.append((start, c - 1))
            start = None

    if start is not None:
        segments.append((start, n_cols - 1))

    return segments


def _looks_numeric(value):
    text = str(value).strip()
    if text == "":
        return False
    text = text.replace(",", "")
    try:
        float(text)
        return True
    except ValueError:
        return False


def _looks_like_header(row_values):
    """Heuristic: header rows are mostly non-numeric strings and mostly unique."""
    non_blank = [v for v in row_values if not _is_blank(v)]

    if not non_blank:
        return False

    non_numeric = sum(1 for v in non_blank if not _looks_numeric(v))
    string_ratio = non_numeric / len(non_blank)

    unique_ratio = len(set(str(v).strip().lower() for v in non_blank)) / len(non_blank)

    return string_ratio >= 0.6 and unique_ratio >= 0.8


def _detect_title(raw_df, row_start, row_end, col_start, col_end):
    """
    If the first row of a block has exactly one non-blank text cell (and the
    block has more rows below it), treat that as a table title, and point
    the caller to the row after it as the real start of the table.
    """
    if row_start >= row_end:
        return None, row_start

    first_row = raw_df.iloc[row_start, col_start:col_end + 1]
    non_blank = [v for v in first_row if not _is_blank(v)]

    if len(non_blank) == 1 and isinstance(non_blank[0], str):
        return str(non_blank[0]).strip(), row_start + 1

    return None, row_start


def _build_dataframe(raw_df, row_start, row_end, col_start, col_end):
    block = raw_df.iloc[row_start:row_end + 1, col_start:col_end + 1].reset_index(drop=True)

    if block.empty:
        return None

    header_values = block.iloc[0].tolist()

    if _looks_like_header(header_values):
        columns = []
        seen = {}

        for i, v in enumerate(header_values):
            name = str(v).strip() if not _is_blank(v) else f"column_{i + 1}"

            if name in seen:
                seen[name] += 1
                name = f"{name}_{seen[name]}"
            else:
                seen[name] = 0

            columns.append(name)

        data = block.iloc[1:].reset_index(drop=True)
        data.columns = columns
    else:
        data = block
        data.columns = [f"column_{i + 1}" for i in range(data.shape[1])]

    data = data.dropna(how="all")
    data = data.loc[:, ~data.isna().all()]

    for col in data.columns:
        converted = pd.to_numeric(
            data[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )
        non_null = data[col].notna().sum()
        if non_null > 0 and converted.notna().sum() >= max(1, int(0.6 * non_null)):
            data[col] = converted

    return data.reset_index(drop=True)


def detect_subtables(raw_df, sheet_name="Sheet1", min_rows=1, min_cols=1):
    """
    Detect one or more logical tables inside a raw (header=None) grid.

    Returns a list of dicts, see module docstring for shape.
    """
    tables = []

    if raw_df is None or raw_df.empty:
        return tables

    row_blocks = _find_row_blocks(raw_df)
    table_counter = 0

    for (row_start, row_end) in row_blocks:
        col_segments = _find_col_segments(raw_df, row_start, row_end)

        for (col_start, col_end) in col_segments:
            title, header_start = _detect_title(raw_df, row_start, row_end, col_start, col_end)

            df = _build_dataframe(raw_df, header_start, row_end, col_start, col_end)

            if df is None:
                continue

            if df.shape[0] < min_rows or df.shape[1] < min_cols:
                continue

            table_counter += 1
            name = title if title else f"{sheet_name}_table{table_counter}"

            tables.append({
                "name": name,
                "sheet": sheet_name,
                "dataframe": df,
                "start_row": header_start,
                "end_row": row_end,
                "start_col": col_start,
                "end_col": col_end,
                "rows": len(df),
                "columns": list(df.columns),
            })

    return tables
