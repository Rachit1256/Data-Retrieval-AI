import {
BarChart,
Bar,
CartesianGrid,
XAxis,
YAxis,
Tooltip,
ResponsiveContainer
}
from "recharts";

function AnalyticsDashboard({ charts }) {

return(

<div>

{

charts.map((chart,index)=>(

<div
key={index}
style={{
height:350,
marginBottom:40,
background:"white",
padding:20,
borderRadius:12
}}
>

<h3>

{chart.title}

</h3>

<ResponsiveContainer>

<BarChart
data={chart.data}
>

<CartesianGrid/>

<XAxis
dataKey={chart.category}
/>

<YAxis/>

<Tooltip/>

<Bar
dataKey={chart.value}
/>

</BarChart>

</ResponsiveContainer>

</div>

))

}

</div>

);

}

export default AnalyticsDashboard;