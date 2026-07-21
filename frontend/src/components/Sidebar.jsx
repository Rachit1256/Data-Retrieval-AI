import { useEffect } from "react";
import api from "../services/api";

function Sidebar({

    files,
    setFiles,

    selectedFile,
    setSelectedFile,

    setSummary,
    setInsights,
    setBusinessInsights,
    setKpis,
    setCharts,
    setVisualizations,
    setExecutive

}) {

    useEffect(() => {

        loadFiles();

    }, []);

    async function loadFiles() {

        try {

            const res = await api.get("/files");

            setFiles(res.data);

        }

        catch (err) {

            console.log(err);

        }

    }

    async function upload(e) {

        const file = e.target.files[0];

        if (!file) return;

        const form = new FormData();

        form.append("file", file);

        try {

            await api.post("/upload", form);

            loadFiles();

        } catch (err) {

            const detail = err?.response?.data?.detail || "Upload failed.";

            alert(detail);

        }

        e.target.value = "";

    }

    async function openFile(file) {

        setSelectedFile(file.filename);

        setSummary(file);

        const [

            insights,

            business,

            kpis,

            charts,

            visuals,

            executive

        ] = await Promise.all([

            api.get(`/insights/${file.filename}`),
            api.get(`/business-insights/${file.filename}`),
            api.get(`/kpis/${file.filename}`),
            api.get(`/analytics/${file.filename}`),
            api.get(`/visualizations/${file.filename}`),
            api.get(`/executive/${file.filename}`)

        ]);

        setInsights(insights.data);
        setBusinessInsights(business.data);
        setKpis(kpis.data);
        setCharts(charts.data);
        setVisualizations(visuals.data);
        setExecutive(executive.data);

    }

    async function clearFiles() {

        await api.delete("/clear");

        setFiles([]);

        setSelectedFile(null);

        setSummary(null);

        setInsights(null);

        setBusinessInsights(null);

        setKpis(null);

        setCharts(null);

        setVisualizations(null);

        setExecutive(null);

    }

    return (

        <div className="sidebar">

            <div className="sidebar-header">

                <h2>📁 My Files</h2>

                <p>

                    Upload and manage spreadsheets

                </p>

            </div>

            <label className="upload-card">

                <div className="upload-icon">

                    ⬆️

                </div>

                <strong>

                    Upload Spreadsheet

                </strong>

                <span>

                    Excel • CSV • PDF

                </span>

                <input

                    type="file"

                    accept=".xlsx,.xls,.csv,.pdf"

                    onChange={upload}

                    hidden

                />

            </label>

            <div className="sidebar-actions">

                <button

                    className="refresh-btn"

                    onClick={loadFiles}

                >

                    Refresh

                </button>

                <button

                    className="clear-btn"

                    onClick={clearFiles}

                >

                    Clear

                </button>

            </div>

            <div className="file-section">

                <h3>

                    Uploaded Files

                </h3>

                <div className="file-list">

                    {

                        files.length === 0

                        ?

                        <div className="empty-files">

                            No spreadsheets uploaded.

                        </div>

                        :

                        files.map(file => (

                            <div

                                key={file.filename}

                                className={

                                    selectedFile === file.filename

                                    ?

                                    "file-card active"

                                    :

                                    "file-card"

                                }

                                onClick={() => openFile(file)}

                            >

                                <div className="file-name">

                                    📄 {file.filename}

                                </div>

                                <div className="file-meta">

                                    {file.rows} rows

                                </div>

                            </div>

                        ))

                    }

                </div>

            </div>

        </div>

    );

}

export default Sidebar;