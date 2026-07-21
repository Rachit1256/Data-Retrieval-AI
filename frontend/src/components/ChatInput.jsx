import { useState } from "react";

function ChatInput({

    onAsk,
    loading

}) {

    const [question, setQuestion] = useState("");

    function submit() {

        const trimmed = question.trim();

        if (!trimmed) return;

        onAsk(trimmed);

        setQuestion("");

    }

    return (

        <div className="chat-input">

            <input

                value={question}

                placeholder="Ask anything about your spreadsheets..."

                onChange={(e)=>setQuestion(e.target.value)}

                onKeyDown={(e)=>{

                    if(e.key==="Enter"){

                        submit();

                    }

                }}

            />

            <button

                onClick={submit}

                disabled={loading}

            >

                {

                    loading

                    ?

                    "Thinking..."

                    :

                    "Ask AI"

                }

            </button>

        </div>

    );

}

export default ChatInput;
