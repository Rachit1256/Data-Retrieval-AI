import { useState } from "react";
import { useDropzone } from "react-dropzone";
import api from "../services/api";

function UploadBox({ onUpload }) {

    const [uploading, setUploading] = useState(false);

    const onDrop = async (acceptedFiles) => {

        if (acceptedFiles.length === 0) return;

        setUploading(true);

        try {

            for (const file of acceptedFiles) {

                const formData = new FormData();

                formData.append("file", file);

                const response = await api.post(
                    "/upload",
                    formData
                );

                onUpload(response.data.files);
            }

        } catch (error) {

            console.log(error);

            alert("Upload Failed");

        }

        setUploading(false);

    };

    const {

        getRootProps,

        getInputProps,

        isDragActive

    } = useDropzone({

        onDrop,

        accept: {

            "application/vnd.ms-excel": [".xls"],

            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],

            "text/csv": [".csv"]

        }

    });

    return (

        <div
            {...getRootProps()}
            style={{
                border: "2px dashed #1976d2",
                padding: 30,
                borderRadius: 15,
                textAlign: "center",
                background: isDragActive ? "#e3f2fd" : "#fafafa",
                cursor: "pointer",
                marginBottom: 20
            }}
        >

            <input {...getInputProps()} />

            {

                uploading ?

                    <h3>Uploading...</h3>

                    :

                    <>
                        <h3>📄 Drop spreadsheets here</h3>

                        <p>or click to browse</p>
                    </>

            }

        </div>

    );

}

export default UploadBox;