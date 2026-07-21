function ResponseCard({ messages, onAsk }) {

    return (

        <>

            {

                messages.map((message, index) => (

                    <div

                        key={index}

                        className={
                            message.role === "user"
                                ? "user-message"
                                : "ai-message"
                        }

                    >

                        <div className="bubble">

                            {message.content &&

                                <p>{message.content}</p>

                            }

                            {message.images && message.images.length > 0 &&

                                <div className="chat-image-grid">

                                    {message.images.map((img, i) => (
                                        <figure key={i} className="chat-image-item">
                                            <img
                                                src={img.url}
                                                alt={img.title || "chart"}
                                                className="chat-image"
                                            />
                                            {img.title &&
                                                <figcaption>{img.title}</figcaption>
                                            }
                                        </figure>
                                    ))}

                                </div>

                            }

                            {message.source &&

                                <div className="message-source">

                                    {message.source}

                                </div>

                            }

                            {

                                message.role === "assistant"

                                &&

                                message.suggestions?.length > 0

                                &&

                                <div className="message-suggestions">

                                    {

                                        message.suggestions.map(

                                            (item, i) => (

                                                <button

                                                    key={i}

                                                    className="suggestion-chip"

                                                    onClick={() => onAsk?.(item)}

                                                >

                                                    {item}

                                                </button>

                                            )

                                        )

                                    }

                                </div>

                            }

                        </div>

                    </div>

                ))

            }

        </>

    );

}

export default ResponseCard;
