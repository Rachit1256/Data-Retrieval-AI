import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";

export default function Layout(props){

    return(

        <div
        style={{
            display:"flex",
            height:"100vh"
        }}
        >

            <Sidebar
                files={props.files}
                upload={props.upload}
                clear={props.clear}
                setFile={props.setFile}
            />

            <ChatWindow
                answer={props.answer}
                question={props.question}
                setQuestion={props.setQuestion}
                ask={props.ask}
                loading={props.loading}
            />

        </div>

    )

}