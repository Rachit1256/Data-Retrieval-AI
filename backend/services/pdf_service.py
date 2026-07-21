from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)

from reportlab.lib.styles import getSampleStyleSheet


def create_pdf(report, filename):

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(

        Paragraph(

            "<b>AI Spreadsheet Report</b>",

            styles["Title"]

        )

    )

    story.append(

        Paragraph(

            f"Generated: {report['generated_at']}",

            styles["Normal"]

        )

    )

    story.append(

        Paragraph(

            f"Rows: {report['rows']}",

            styles["Normal"]

        )

    )

    story.append(

        Paragraph(

            f"Columns: {len(report['columns'])}",

            styles["Normal"]

        )

    )

    story.append(

        Paragraph(

            "<b>Business Insights</b>",

            styles["Heading2"]

        )

    )

    for tip in report["insights"]:

        story.append(

            Paragraph(

                "• " + tip,

                styles["Normal"]

            )

        )

    pdf.build(story)

    return filename