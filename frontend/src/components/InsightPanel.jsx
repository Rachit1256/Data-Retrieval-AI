import ChartRenderer from "./ChartRenderer";

function InsightPanel({

    summary,
    insights,
    businessInsights,
    kpis,
    charts,
    visualizations,
    executive,
    selectedFile

}) {

    if (!summary) {

        return (

            <aside className="insight">

                <div className="empty-dashboard">

                    <div className="dashboard-icon">

                        📊

                    </div>

                    <h2>

                        Analytics Dashboard

                    </h2>

                    <p>

                        Upload or select a spreadsheet to view
                        AI-generated analytics, KPIs and charts.

                    </p>

                </div>

            </aside>

        );

    }

    return (

        <aside className="insight">

            {/* ============================= */}
            {/* Dashboard Header */}
            {/* ============================= */}

            <div className="dashboard-header">

                <div>

                    <h2>

                        Analytics Dashboard

                    </h2>

                    <p>

                        {selectedFile}

                    </p>

                </div>

                <div className="dataset-pill">

                    {summary.rows} Rows

                </div>

            </div>

            {/* ============================= */}
            {/* Executive Summary */}
            {/* ============================= */}

            <section className="executive-card">

                <div className="section-title">

                    <h2>Executive Summary</h2>

                </div>

                {

                    !executive ||

                    executive.length === 0

                    ?

                    <p>

                        No executive summary generated.

                    </p>

                    :

                    <ul className="executive-list">

                        {

                            executive.map((item, index) => (

                                <li key={index}>

                                    {item}

                                </li>

                            ))

                        }

                    </ul>

                }

            </section>


            {/* ============================= */}
            {/* Dataset Overview */}
            {/* ============================= */}

            <section className="panel-card">

                <div className="section-title">

                    <h2>📁 Dataset Overview</h2>

                </div>

                <div className="dataset-grid">

                    <div className="dataset-item">

                        <span>

                            Rows

                        </span>

                        <strong>

                            {summary.rows}

                        </strong>

                    </div>

                    <div className="dataset-item">

                        <span>

                            Columns

                        </span>

                        <strong>

                            {(summary.columns || []).length}

                        </strong>

                    </div>

                    <div className="dataset-item">

                        <span>

                            Uploaded

                        </span>

                        <strong>

                            {summary.uploaded_at}

                        </strong>

                    </div>

                </div>

            </section>

            {/* ============================= */}
            {/* Dataset Columns */}
            {/* ============================= */}

            <section className="panel-card">

                <div className="section-title">

                    <h2>🏷 Dataset Columns</h2>

                </div>

                <div className="tags">

                    {

                        (summary.columns || []).map(col => (

                            <span

                                key={col}

                                className="tag"

                            >

                                {col}

                            </span>

                        ))

                    }

                </div>

            </section>
                        {/* ============================= */}
            {/* Statistics */}
            {/* ============================= */}

            <section className="panel-card">

                <div className="section-title">

                    <h2>📊 Statistical Overview</h2>

                </div>

                {

                    insights?.statistics &&

                    Object.keys(insights.statistics).length > 0

                    ?

                    <div className="stats-grid">

                        {

                            Object.entries(

                                insights.statistics

                            ).map(

                                ([name, stat]) => (

                                    <div

                                        key={name}

                                        className="stat-card"

                                    >

                                        <h4>

                                            {name}

                                        </h4>

                                        <div className="stat-row">

                                            <span>

                                                Average

                                            </span>

                                            <strong>

                                                {Number(
                                                    stat.average
                                                ).toFixed(2)}

                                            </strong>

                                        </div>

                                        <div className="stat-row">

                                            <span>

                                                Median

                                            </span>

                                            <strong>

                                                {stat.median}

                                            </strong>

                                        </div>

                                        <div className="stat-row">

                                            <span>

                                                Minimum

                                            </span>

                                            <strong>

                                                {stat.minimum}

                                            </strong>

                                        </div>

                                        <div className="stat-row">

                                            <span>

                                                Maximum

                                            </span>

                                            <strong>

                                                {stat.maximum}

                                            </strong>

                                        </div>

                                        <div className="stat-row">

                                            <span>

                                                Sum

                                            </span>

                                            <strong>

                                                {stat.sum}

                                            </strong>

                                        </div>

                                    </div>

                                )

                            )

                        }

                    </div>

                    :

                    <div className="empty-card">

                        No statistics available.

                    </div>

                }

            </section>

            {/* ============================= */}
            {/* Business Insights */}
            {/* ============================= */}

            <section className="panel-card">

                <div className="section-title">

                    <h2>💼 Business Insights</h2>

                </div>

                {

                    (businessInsights || []).length === 0

                    ?

                    <div className="empty-card">

                        No business insights generated.

                    </div>

                    :

                    <div className="timeline">

                        {

                            businessInsights.map(

                                (item, index) => (

                                    <div

                                        key={index}

                                        className="timeline-item"

                                    >

                                        <div className="timeline-dot">

                                            💡

                                        </div>

                                        <div className="timeline-content">

                                            {item}

                                        </div>

                                    </div>

                                )

                            )

                        }

                    </div>

                }

            </section>

            {/* ============================= */}
            {/* Interactive Charts */}
            {/* ============================= */}

            <section className="panel-card">

                <div className="section-title">

                    <h2>📈 Interactive Charts</h2>

                </div>

                {

                    (charts || []).length === 0

                    ?

                    <div className="empty-card">

                        No chart data available.

                    </div>

                    :

                    <div className="chart-grid">

                        {

                            charts.map(

                                (chart, index) => (

                                    <div

                                        key={index}

                                        className="chart-card"

                                    >

                                        <ChartRenderer

                                            chart={chart}

                                        />

                                    </div>

                                )

                            )

                        }

                    </div>

                }

            </section>
                        {/* ============================= */}
            {/* Suggested Visualizations */}
            {/* ============================= */}

            <section className="panel-card">

                <div className="section-title">

                    🎨 Suggested Visualizations

                </div>

                {

                    (visualizations || []).length === 0

                    ?

                    <div className="empty-card">

                        No visualization recommendations.

                    </div>

                    :

                    <div className="visual-grid">

                        {

                            visualizations.map((chart, index) => (

                                <div

                                    key={index}

                                    className="visual-card"

                                >

                                    <div className="visual-icon">

                                        {

                                            chart.type === "bar"

                                            ? "📊"

                                            : chart.type === "line"

                                            ? "📈"

                                            : chart.type === "pie"

                                            ? "🥧"

                                            : chart.type === "scatter"

                                            ? "🔵"

                                            : "📉"

                                        }

                                    </div>

                                    <div className="visual-info">

                                        <strong>

                                            {chart.type.toUpperCase()}

                                        </strong>

                                        <p>

                                            {chart.title}

                                        </p>

                                    </div>

                                </div>

                            ))

                        }

                    </div>

                }

            </section>

            

            

        </aside>

    );

}

export default InsightPanel;