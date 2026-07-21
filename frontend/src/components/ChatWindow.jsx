import { useEffect, useRef, useState } from "react";
import ResponseCard from "./ResponseCard";
import ChatInput from "./ChatInput";
import api, { chartUrl } from "../services/api";

function ChatWindow({

    messages,
    setMessages

}) {

    const messagesEndRef = useRef(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {

        messagesEndRef.current?.scrollIntoView({

            behavior: "smooth"

        });

    }, [messages]);

    // Shared by both the text input and the suggestion chips, so
    // clicking a suggestion actually sends it instead of just
    // filling the input box.
    async function sendQuestion(question) {

        const currentQuestion = (question ?? "").trim();

        if (!currentQuestion || loading) return;

        setMessages(prev => [
            ...prev,
            {
                role: "user",
                content: currentQuestion
            }
        ]);

        setLoading(true);

        try {

            const response = await api.post("/chat", {
                question: currentQuestion
            });

            const charts = response.data.charts || [];

            const images = charts.map(c => ({
                url: chartUrl(c.image),
                title: c.title,
                type: c.type
            }));

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: response.data.answer,
                    image: images[0]?.url,
                    images,
                    source: response.data.source,
                    suggestions: response.data.suggestions || []
                }
            ]);

        }

        catch {

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "❌ Unable to contact backend."
                }
            ]);

        }

        setLoading(false);

    }

    return (

        <main className="chat">

            <div className="chat-header">

                <div>

                    <p>

                        Ask questions about your uploaded spreadsheets

                    </p>

                </div>

                <div className="chat-count">

                    {messages.length} Messages

                </div>

            </div>

            <div className="messages">

                {

                    messages.length === 0 ?

                        <div className="empty-chat">

                            <div className="empty-icon">

                                🤖

                            </div>

                            <h2>

                                Welcome to AskAI

                            </h2>

                            <p>

                                Upload a spreadsheet and start asking questions.

                            </p>

                        </div>

                        :

                        <ResponseCard

                            messages={messages}
                            onAsk={sendQuestion}

                        />

                }

                <div ref={messagesEndRef}></div>

            </div>

            <ChatInput

                onAsk={sendQuestion}
                loading={loading}

            />

        </main>

    );

}

export default ChatWindow;
