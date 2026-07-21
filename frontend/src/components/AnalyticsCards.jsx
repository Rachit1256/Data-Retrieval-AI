function AnalyticsCards({ files }) {

    return (

        <div>
            
            <h2>Overview</h2>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 15
                }}
            >

                <Card
                    title="Files"
                    value={files.length}
                />

                <Card
                    title="AI"
                    value="Ready"
                />

            </div>

        </div>

    );

}

function Card({ title, value }) {

    return (

        <div
            style={{
                padding: 20,
                borderRadius: 12,
                background: "#f5f5f5"
            }}
        >

            <h3>{title}</h3>

            <h1>{value}</h1>

        </div>

    );

}

export default AnalyticsCards;