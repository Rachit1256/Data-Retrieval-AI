import { useState } from "react";

import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import InsightPanel from "../components/InsightPanel";

import "../styles/dashboard.css";

function Dashboard() {

    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);

    const [messages, setMessages] = useState([
        {
            role: "assistant",
            content: "👋 Welcome! Upload a spreadsheet to begin."
        }
    ]);

    const [summary, setSummary] = useState(null);
    const [insights, setInsights] = useState(null);
    const [businessInsights, setBusinessInsights] = useState(null);
    const [kpis, setKpis] = useState(null);
    const [charts, setCharts] = useState(null);
    const [visualizations, setVisualizations] = useState(null);
    const [executive, setExecutive] = useState(null);

    return (

        <div className="dashboard">

            {/* LEFT SIDEBAR */}

            <aside className="dashboard-sidebar">

                <Sidebar

                    files={files}
                    setFiles={setFiles}

                    selectedFile={selectedFile}
                    setSelectedFile={setSelectedFile}

                    setSummary={setSummary}
                    setInsights={setInsights}
                    setBusinessInsights={setBusinessInsights}
                    setKpis={setKpis}
                    setCharts={setCharts}
                    setVisualizations={setVisualizations}
                    setExecutive={setExecutive}

                />

            </aside>

            {/* CENTER */}

            <main className="dashboard-main">

                <Header />

                <ChatWindow

                    messages={messages}
                    setMessages={setMessages}

                />

            </main>

            {/* RIGHT */}

            <aside className="dashboard-right">

                <InsightPanel

                    selectedFile={selectedFile}

                    summary={summary}
                    insights={insights}
                    businessInsights={businessInsights}
                    kpis={kpis}
                    charts={charts}
                    visualizations={visualizations}
                    executive={executive}

                />

            </aside>

        </div>

    );

}

export default Dashboard;