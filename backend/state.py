documents = {}

conversation = []

last_question = ""

last_result = None

last_chart = None

last_metric = None

last_column = None

MAX_HISTORY = 20

# ---------------------------------------------------------------------
# New: fine-grained table registry.
#
# state.files:  { filename: {filename, type, uploaded_at, table_ids: [...]} }
# state.tables: { table_id: {id, filename, sheet, name, dataframe, rows, columns} }
#
# Every subtable detected inside every uploaded file (an Excel sheet, a
# CSV, or a page of a PDF) gets its own entry in state.tables, so it can
# be queried, compared, and visualized independently. `documents` above
# is kept for backwards compatibility with the existing insights/KPI/
# report pipeline, which still operates on one "primary" dataframe per
# uploaded file.
# ---------------------------------------------------------------------

files = {}

tables = {}
