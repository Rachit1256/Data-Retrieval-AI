import api from "../services/api";

function ReportButton({ filename }) {

    function download(type){

        window.open(

            `${api.defaults.baseURL}/report/${type}/${filename}`

        );

    }

    return(

        <div>

            <button onClick={()=>download("pdf")}>

                PDF

            </button>

            <button onClick={()=>download("docx")}>

                Word

            </button>

            <button onClick={()=>download("excel")}>

                Excel

            </button>

        </div>

    );

}

export default ReportButton;