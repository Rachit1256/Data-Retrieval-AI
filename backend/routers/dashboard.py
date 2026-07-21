from fastapi import APIRouter, HTTPException

from services import table_registry, data_tools

router = APIRouter()


@router.get("/dashboard/{table_id}")
def dashboard_for_table(table_id: str):
    """Build a dashboard (KPIs + charts) for one specific table_id.
    Get valid table_ids from GET /tables or GET /tables/{filename}."""

    if table_registry.get_table(table_id) is None:
        raise HTTPException(status_code=404, detail="Table not found. Call /tables to list valid table_ids.")

    data_tools.reset_capture()
    result = data_tools.build_dashboard(table_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/dashboard/file/{filename}")
def dashboard_for_file(filename: str):
    """Convenience: build a dashboard for the largest detected table in a
    given uploaded file, without needing to know its table_id."""

    primary = table_registry.largest_table_for_file(filename)

    if primary is None:
        raise HTTPException(status_code=404, detail="File not found or has no detected tables.")

    data_tools.reset_capture()
    result = data_tools.build_dashboard(primary["id"])

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
