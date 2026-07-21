"""
chat_agent.py

The actual chat "brain". Replaces the old stack of keyword-matching
services (intent_service -> analysis_service / analyst_service /
query_service -> RAG fallback) with a single Gemini call that has real
tools (services/data_tools.py) grounded in the table registry.

Why this fixes "wrong or generic answers": before, the chatbot guessed
intent from substrings like "sum" or "salary" and each heuristic could
silently misfire or shadow the others. Now Gemini sees the *actual*
schema of your uploaded tables (via list_tables/get_table_preview) and
decides which tool to call -- aggregate, group_aggregate, compare_tables,
filter_rows, create_chart, build_dashboard, or search_documents -- and
those tools run plain, deterministic pandas underneath. The model never
invents numbers; it only ever reports what a tool actually returned.

If GEMINI_API_KEY is missing/invalid or the model call fails for any
reason, this returns a clear error message instead of crashing the
/chat endpoint, so failures are visible instead of looking like "the
chatbot just doesn't work".
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from services import data_tools

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """You are a data analyst assistant embedded in a spreadsheet / CSV / PDF chat app.

You have tools to inspect and compute over the user's uploaded data. Always use them -- never guess or make up numbers.

Rules:
- If you don't already know the exact table_id and column names, call list_tables() and/or get_table_preview() first. Never invent a table_id or column name -- use the ones the tools actually return.
- For totals/averages/counts/max/min on one table, use aggregate().
- For breakdowns like "X by Y" (sales by region, average salary by department), use group_aggregate().
- For comparing the same metric across two or more tables/sheets/time periods, use compare_tables().
- For conditional row lookups ("employees earning more than 50000", "orders from California"), use filter_rows().
- For any request to plot/chart/graph/visualize something, actually call create_chart() -- never just describe a chart in words.
- For "build a dashboard" / "give me an overview" requests, call build_dashboard().
- For open-ended questions not covered by the above (e.g. about PDF text content), use search_documents().
- If a tool returns an error, say so plainly and ask for the specific missing detail (e.g. the exact column name) -- don't silently fall back to a generic answer.
- Keep answers concise. Use bullet points for lists of numbers or grouped results.
- When you used create_chart() or build_dashboard(), don't re-describe the chart in exhaustive detail -- summarize what it shows in one or two sentences; the image itself is shown separately in the UI.
"""


def _history_to_contents(conversation_history, question):
    contents = []

    for msg in conversation_history[-10:]:
        role = "model" if msg.get("role") == "assistant" else "user"
        text = msg.get("content", "")
        if not isinstance(text, str):
            text = str(text)
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))

    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    return contents


def run_agent(question, conversation_history=None):
    """
    Returns {"answer": str, "charts": [ {image, type, title}, ... ], "error": str|None}
    """

    data_tools.reset_capture()

    if not os.getenv("GEMINI_API_KEY"):
        return {
            "answer": "GEMINI_API_KEY is not set on the backend (.env), so I can't reach the AI model. "
                      "Set it and restart the server.",
            "charts": [],
            "error": "missing_api_key",
        }

    contents = _history_to_contents(conversation_history or [], question)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=data_tools.ALL_TOOLS,
            ),
        )
    except Exception as exc:
        return {
            "answer": f"I couldn't complete that request -- the AI model call failed: {exc}",
            "charts": [],
            "error": str(exc),
        }

    answer = getattr(response, "text", None)

    if not answer:
        answer = "I wasn't able to generate a response for that -- try rephrasing the question."

    return {
        "answer": answer,
        "charts": data_tools.get_captured_charts(),
        "error": None,
    }
