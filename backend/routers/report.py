from fastapi import APIRouter
from fastapi.responses import FileResponse

import state

from services.report_service import build_report
from services.pdf_service import create_pdf
from services.docx_service import create_docx
from services.excel_export_service import export_excel

router = APIRouter()


@router.get("/report/pdf/{filename}")
def pdf(filename: str):

    document = state.documents[filename]

    report = build_report(document)

    output = f"reports/{filename}.pdf"

    create_pdf(report, output)

    return FileResponse(
        output,
        media_type="application/pdf",
        filename=f"{filename}.pdf"
    )


@router.get("/report/docx/{filename}")
def docx(filename: str):

    document = state.documents[filename]

    report = build_report(document)

    output = f"reports/{filename}.docx"

    create_docx(report, output)

    return FileResponse(
        output,
        filename=f"{filename}.docx"
    )


@router.get("/report/excel/{filename}")
def excel(filename: str):

    document = state.documents[filename]

    report = build_report(document)

    output = f"reports/{filename}_summary.xlsx"

    export_excel(report, output)

    return FileResponse(
        output,
        filename=f"{filename}_summary.xlsx"
    )