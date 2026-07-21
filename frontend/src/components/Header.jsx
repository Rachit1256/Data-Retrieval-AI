import { useEffect, useState } from "react";

function Header() {

    const [time, setTime] = useState("");

    useEffect(() => {

        const update = () => {

            const now = new Date();

            setTime(
                now.toLocaleString("en-IN", {
                    day: "2-digit",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit"
                })
            );

        };

        update();

        const timer = setInterval(update, 1000);

        return () => clearInterval(timer);

    }, []);

    return (

        <header className="header">

            <div className="header-left">

                <div className="logo-circle">

                    🤖

                </div>

                <div>

                    <h1>AskAI Analytics</h1>

                </div>

            </div>

            <div className="header-right">

                <div className="status">

                    <span className="status-dot"></span>

                    AI Online

                </div>

                <div className="current-time">

                    {time}

                </div>

            </div>

        </header>

    );

}

export default Header;