from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from datetime import datetime

import state
from services.file_loader import load_file, SUPPORTED_EXTENSIONS
from services import table_registry
from services.rag_service import clear_database, add_table, add_text
from services.analytics_service import generate_chart_data
from services.insight_service import generate_insights
from services.business_insight_service import generate_business_insights
from services.kpi_service import detect_kpis
from services.visualization_service import detect_visualizations
from services.executive_summary import executive_summary

router = APIRouter()


@router.post("/upload")
async def upload(file: UploadFile = File(...)):

    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = load_file(path, file.filename)

    table_registry.register_file(file.filename, result["type"])

    registered_tables = []

    for table in result["tables"]:
        table_id = table_registry.register_table(file.filename, table)
        add_table(table_id, file.filename, table["name"], table["dataframe"])

        registered_tables.append({
            "table_id": table_id,
            "name": table["name"],
            "sheet": table["sheet"],
            "rows": table["rows"],
            "columns": table["columns"],
        })

    for chunk in result.get("text_chunks", []):
        add_text(
            doc_id=f"{file.filename}_page{chunk['page']}",
            filename=file.filename,
            text=chunk["text"],
            extra_meta={"page": chunk["page"]}
        )

    response = {
        "message": "Upload Successful",
        "filename": file.filename,
        "type": result["type"],
        "files": table_registry.list_files(),
        "tables": registered_tables,
    }

    # ------------------------------------------------------------------
    # Backwards compatibility: existing insights/KPI/chart/report pipeline
    # expects exactly one dataframe per filename in state.documents. Feed
    # it the largest detected table so those features keep working
    # unchanged for spreadsheets/CSVs. PDFs with no tables simply won't
    # populate this (they're still searchable via chat/RAG).
    # ------------------------------------------------------------------
    primary = table_registry.largest_table_for_file(file.filename)

    if primary is not None:
        df = primary["dataframe"]

        insights = generate_insights(df)
        business = generate_business_insights(df)
        kpis = detect_kpis(df)
        charts = generate_chart_data(df)
        visualizations = detect_visualizations(df)
        executive = executive_summary(df)

        state.documents[file.filename] = {
            "data": df,
            "rows": len(df),
            "columns": list(df.columns),
            "uploaded_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "insights": insights,
            "business_insights": business,
            "kpis": kpis,
            "charts": charts,
            "visualizations": visualizations,
            "executive": executive,
        }

        response.update({
            "summary": {
                "rows": len(df),
                "columns": list(df.columns),
                "uploaded_at": state.documents[file.filename]["uploaded_at"],
            },
            "insights": insights,
            "business_insights": business,
            "kpis": kpis,
            "charts": charts,
            "visualizations": visualizations,
        })

    print("========== FILE UPLOADED ==========")
    print(f"{file.filename}: {len(registered_tables)} table(s) detected")

    return response


@router.get("/files")
def get_files():
    return table_registry.list_files()


@router.get("/tables")
def get_all_tables():
    return [
        {
            "table_id": t["id"],
            "filename": t["filename"],
            "sheet": t["sheet"],
            "name": t["name"],
            "rows": t["rows"],
            "columns": t["columns"],
        }
        for t in table_registry.list_all_tables()
    ]


@router.get("/tables/{filename}")
def get_tables_for_file(filename: str):
    tables = table_registry.list_tables_for_file(filename)

    if not tables:
        raise HTTPException(status_code=404, detail="File not found or has no detected tables.")

    return [
        {
            "table_id": t["id"],
            "sheet": t["sheet"],
            "name": t["name"],
            "rows": t["rows"],
            "columns": t["columns"],
        }
        for t in tables
    ]


@router.get("/table/{table_id}/preview")
def preview_table(table_id: str, limit: int = 50):
    table = table_registry.get_table(table_id)

    if table is None:
        raise HTTPException(status_code=404, detail="Table not found.")

    df = table["dataframe"]

    return {
        "table_id": table_id,
        "name": table["name"],
        "columns": table["columns"],
        "rows": len(df),
        "preview": df.head(limit).to_dict("records"),
    }


@router.get("/insights/{filename}")
def get_insights(filename: str):
    if filename not in state.documents:
        return {"error": "Spreadsheet not found."}
    return state.documents[filename]["insights"]


@router.delete("/clear")
def clear():
    state.documents.clear()
    table_registry.clear_all()
    clear_database()

    return {"message": "All uploaded files removed."}


@router.delete("/files/{filename}")
def delete_file(filename: str):
    if filename in state.documents:
        del state.documents[filename]

    table_registry.remove_file(filename)

    return {"message": f"{filename} removed."}


@router.get("/business-insights/{filename}")
def business_insights(filename: str):
    if filename not in state.documents:
        return {"error": "Spreadsheet not found."}
    return state.documents[filename]["business_insights"]


@router.get("/kpis/{filename}")
def get_kpis(filename: str):
    if filename not in state.documents:
        return {"error": "Spreadsheet not found."}
    return state.documents[filename]["kpis"]


@router.get("/analytics/{filename}")
def analytics(filename: str):
    if filename not in state.documents:
        return {"error": "File not found."}
    return state.documents[filename]["charts"]


@router.get("/visualizations/{filename}")
def visualizations(filename: str):
    if filename not in state.documents:
        return {"error": "File not found."}
    return state.documents[filename]["visualizations"]


@router.get("/correlation/{filename}")
def correlation(filename: str):
    if filename not in state.documents:
        return {"error": "File not found."}

    from services.correlation_service import correlation as compute_correlation
    df = state.documents[filename]["data"]

    return compute_correlation(df)


@router.get("/executive/{filename}")
def executive(filename: str):
    if filename not in state.documents:
        return {"error": "Spreadsheet not found."}
    return state.documents[filename]["executive"]
