"""
suggestion_service.py

Generates the follow-up "suggestion chips" shown under each chat reply.

The old version only looked at keywords in the current question string
("salary" -> a fixed hardcoded list, "revenue" -> a different fixed
list, etc.) -- it never looked at the data that was actually uploaded,
and had no idea what had already been asked, so it would happily
re-suggest the same question forever.

This version is grounded in two things instead:
  1. The real schema of whatever tables are currently registered
     (services/table_registry) -- so suggestions reference actual
     column names that exist in your data, not generic placeholders.
  2. Recent conversation history -- so it avoids repeating a question
     that was just asked, and can suggest logical next steps (a
     drill-down, a comparison, a chart of what was just computed, a
     dashboard) instead of a static list.

One Gemini call, asked for strict JSON (a plain list of short question
strings). If that call fails for any reason (no API key, network,
malformed response), a schema-derived fallback still produces sensible,
data-aware suggestions without needing the model at all -- so this never
just goes blank.
"""

import os
import re
import json

import pandas as pd
from dotenv import load_dotenv
from google import genai

from services import table_registry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"
MAX_SUGGESTIONS = 5
MAX_HISTORY_TURNS = 8
MAX_SCHEMA_TABLES = 6


def _schema_summary():
    tables = table_registry.list_all_tables()[:MAX_SCHEMA_TABLES]

    lines = []
    for t in tables:
        columns = ", ".join(str(c) for c in t["columns"][:15])
        lines.append(f"- \"{t['name']}\" ({t['rows']} rows): columns = [{columns}]")

    return "\n".join(lines)


def _history_summary(conversation_history):
    lines = []
    for msg in (conversation_history or [])[-MAX_HISTORY_TURNS:]:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = str(msg.get("content", ""))[:400]
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def _parse_json_list(text):
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())

    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(parsed, list):
        return None

    cleaned = [str(item).strip() for item in parsed if str(item).strip()]
    return cleaned or None


def _fallback_suggestions():
    """Pure schema-derived suggestions, no LLM call -- used if the model
    call fails or GEMINI_API_KEY isn't set, so suggestions never go
    blank or generic."""

    tables = table_registry.list_all_tables()

    if not tables:
        return []

    table = max(tables, key=lambda t: t["rows"])
    df = table["dataframe"]

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    suggestions = []

    if numeric_cols:
        suggestions.append(f"What is the total {numeric_cols[0]}?")
        suggestions.append(f"What is the average {numeric_cols[0]}?")

    if categorical_cols and numeric_cols:
        suggestions.append(f"Show {numeric_cols[0]} by {categorical_cols[0]}")
        suggestions.append(f"Plot a bar chart of {numeric_cols[0]} by {categorical_cols[0]}")
    elif categorical_cols:
        suggestions.append(f"Show the distribution of {categorical_cols[0]}")

    suggestions.append("Build a dashboard for this data")

    return suggestions[:MAX_SUGGESTIONS]


def generate_suggestions(question, answer="", conversation_history=None):
    """
    question: the question that was just asked (string)
    answer:   the answer that was just given (string, optional)
    conversation_history: list of {"role": "user"|"assistant", "content": str}
    """

    if not table_registry.list_all_tables():
        return []

    if not os.getenv("GEMINI_API_KEY"):
        return _fallback_suggestions()

    schema = _schema_summary()
    history = _history_summary(conversation_history)

    prompt = f"""You suggest follow-up questions for a data-analysis chatbot, shown as clickable chips under its last reply.

Available data (only reference columns that actually appear here):
{schema}

Recent conversation (most recent last):
{history}

Most recent exchange:
User: {question}
Assistant: {answer}

Suggest {MAX_SUGGESTIONS} short follow-up questions the user might click next. Rules:
- Each must reference real column/table names from the schema above -- never invent a column.
- Do NOT repeat or closely rephrase any question already asked in the conversation above.
- Vary the type: mix in a drill-down/filter, a comparison or breakdown, a chart/visualization request, and (if not already built) a dashboard request.
- Keep each under 10 words, phrased as a question or short command a user would naturally type.
- Respond with ONLY a JSON array of strings, nothing else -- no markdown, no code fences, no explanation.
"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        parsed = _parse_json_list(response.text)

        if parsed:
            return parsed[:MAX_SUGGESTIONS]
    except Exception:
        pass

    return _fallback_suggestions()
