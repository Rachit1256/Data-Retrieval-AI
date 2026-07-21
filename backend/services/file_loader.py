"""
file_loader.py

Single entry point for turning an uploaded file (xlsx / xls / csv / pdf)
into a list of clean, named tables (see subtable_detector.py) plus, for
PDFs, raw text chunks that get indexed for RAG/chat but aren't tabular.

Usage:
    from services.file_loader import load_file
    result = load_file(path, filename)
    # result == {
    #   "type": "excel" | "csv" | "pdf",
    #   "tables": [ {name, sheet, dataframe, rows, columns, ...}, ... ],
    #   "text_chunks": [ {"page": 1, "text": "..."}, ... ]  # pdf only
    # }
"""

import os
import pandas as pd

from services.subtable_detector import detect_subtables

try:
    import pdfplumber
except ImportError:  # pdfplumber is optional until requirements are reinstalled
    pdfplumber = None


SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv", ".pdf"}


def load_file(path, filename=None):
    filename = filename or os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()

    if ext in (".xlsx", ".xls"):
        return _load_excel(path)

    if ext == ".csv":
        return _load_csv(path)

    if ext == ".pdf":
        return _load_pdf(path)

    raise ValueError(
        f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )


def _load_excel(path):
    xls = pd.ExcelFile(path)
    tables = []

    for sheet_name in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)

        if raw.empty:
            continue

        tables.extend(detect_subtables(raw, sheet_name=sheet_name))

    return {"type": "excel", "tables": tables, "text_chunks": []}


def _load_csv(path):
    # Try a couple of common encodings/delimiters before giving up.
    raw = None
    for kwargs in ({}, {"sep": ";"}, {"encoding": "latin1"}):
        try:
            raw = pd.read_csv(path, header=None, **kwargs)
            if raw.shape[1] > 1 or kwargs:
                break
        except Exception:
            continue

    if raw is None:
        raw = pd.read_csv(path, header=None)

    tables = detect_subtables(raw, sheet_name="csv")
    return {"type": "csv", "tables": tables, "text_chunks": []}


def _load_pdf(path):
    if pdfplumber is None:
        raise RuntimeError(
            "PDF support requires pdfplumber. Install it with: pip install pdfplumber"
        )

    tables = []
    text_chunks = []

    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""

            if page_text.strip():
                text_chunks.append({"page": page_num, "text": page_text})

            extracted = page.extract_tables()

            for t_idx, raw_table in enumerate(extracted, start=1):
                if not raw_table or len(raw_table) < 2:
                    continue

                raw_df = pd.DataFrame(raw_table)
                sub = detect_subtables(raw_df, sheet_name=f"page{page_num}")

                for s in sub:
                    s["name"] = f"page{page_num}_table{t_idx}" if len(sub) == 1 else s["name"]
                    tables.append(s)

    return {"type": "pdf", "tables": tables, "text_chunks": text_chunks}
