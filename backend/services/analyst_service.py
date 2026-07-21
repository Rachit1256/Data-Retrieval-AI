import pandas as pd


def analyst_report(df: pd.DataFrame, question: str):

    report = []

    q = question.lower()

    numeric = df.select_dtypes(include="number")

    # -------------------------
    # Salary
    # -------------------------

    if "salary" in q and "salary" in df.columns:

        avg = df["salary"].mean()

        report.append(
            f"Average Salary: {avg:.2f}"
        )

        report.append(
            f"Highest Salary: {df['salary'].max()}"
        )

        report.append(
            f"Lowest Salary: {df['salary'].min()}"
        )

        report.append(
            f"Employees Above Average: {(df['salary']>avg).sum()}"
        )

        report.append(
            "Suggested Questions:"
        )

        report.append(
            "• Show salary distribution"
        )

        report.append(
            "• Compare salary by department"
        )

        return "\n".join(report)

    # -------------------------
    # Revenue
    # -------------------------

    if "revenue" in q and "revenue" in df.columns:

        avg = df["revenue"].mean()

        report.append(
            f"Total Revenue: {df['revenue'].sum():,.2f}"
        )

        report.append(
            f"Average Revenue: {avg:.2f}"
        )

        report.append(
            f"Maximum Revenue: {df['revenue'].max()}"
        )

        report.append(
            "Suggested Questions:"
        )

        report.append(
            "• Plot revenue trend"
        )

        report.append(
            "• Compare revenue by region"
        )

        return "\n".join(report)

    return None