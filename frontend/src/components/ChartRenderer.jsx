import {

    ResponsiveContainer,

    BarChart,

    Bar,

    PieChart,

    Pie,

    Cell,

    LineChart,

    Line,

    CartesianGrid,

    XAxis,

    YAxis,

    Tooltip,

    Legend

} from "recharts";

const COLORS = [

    "#2563eb",
    "#16a34a",
    "#f59e0b",
    "#dc2626",
    "#9333ea",
    "#0891b2"

];

function ChartRenderer({ chart }) {

    if (!chart || !chart.data || chart.data.length === 0) {

        return (

            <div className="chart-empty">

                No chart data available.

            </div>

        );

    }

    return (

        <div className="chart-container">

            <div className="chart-header">

                <h4>

                    {chart.title}

                </h4>

                <span>

                    {chart.type
                        ? chart.type.toUpperCase()
                        : "BAR"}

                </span>

            </div>

            <div className="chart-body">

                <ResponsiveContainer
                    width="100%"
                    height={300}
                >

                    {

                        chart.type === "pie"

                        ?

                        (

                            <PieChart>

                                <Pie

                                    data={chart.data}

                                    dataKey={chart.value}

                                    nameKey={chart.category}

                                    outerRadius={100}

                                    label

                                >

                                    {

                                        chart.data.map((entry, index) => (

                                            <Cell

                                                key={index}

                                                fill={
                                                    COLORS[
                                                        index %
                                                        COLORS.length
                                                    ]
                                                }

                                            />

                                        ))

                                    }

                                </Pie>

                                <Tooltip />

                                <Legend />

                            </PieChart>

                        )

                        :

                        chart.type === "line"

                        ?

                        (

                            <LineChart

                                data={chart.data}

                            >

                                <CartesianGrid

                                    strokeDasharray="3 3"

                                />

                                <XAxis

                                    dataKey={chart.category}

                                />

                                <YAxis />

                                <Tooltip />

                                <Legend />

                                <Line

                                    type="monotone"

                                    dataKey={chart.value}

                                    stroke="#2563eb"

                                    strokeWidth={3}

                                />

                            </LineChart>

                        )

                        :

                        (

                            <BarChart

                                data={chart.data}

                            >

                                <CartesianGrid

                                    strokeDasharray="3 3"

                                />

                                <XAxis

                                    dataKey={chart.category}

                                />

                                <YAxis />

                                <Tooltip />

                                <Legend />

                                <Bar

                                    dataKey={chart.value}

                                    fill="#2563eb"

                                    radius={[6, 6, 0, 0]}

                                />

                            </BarChart>

                        )

                    }

                </ResponsiveContainer>

            </div>

        </div>

    );

}

export default ChartRenderer;