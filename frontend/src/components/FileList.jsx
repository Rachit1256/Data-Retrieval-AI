function FileList({ files }) {

    return (

        <div>

            <h3>Uploaded Files</h3>

            {

                files.map((file) => (

                    <div
                        key={file}
                        style={{
                            padding: 12,
                            marginBottom: 10,
                            borderRadius: 10,
                            background: "#ECEFF1"
                        }}
                    >

                        📄 {file}

                    </div>

                ))

            }

        </div>

    );

}

export default FileList;