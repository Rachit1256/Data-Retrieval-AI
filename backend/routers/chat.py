from fastapi import APIRouter
from pydantic import BaseModel

import state
from services.suggestion_service import generate_suggestions
from services.context_service import resolve_context
from services.chat_agent import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):

    request.question = resolve_context(request.question)
    state.last_question = request.question

    state.conversation.append({"role": "user", "content": request.question})

    if len(state.conversation) > state.MAX_HISTORY:
        state.conversation.pop(0)

    if len(state.tables) == 0:
        return {
            "answer": "Please upload one or more spreadsheets, CSVs, or PDFs first.",
            "charts": [],
            "suggestions": generate_suggestions(request.question, "", state.conversation),
        }

    # history excludes the message we just appended -- run_agent adds the
    # current question as the final turn itself.
    history = state.conversation[:-1]

    result = run_agent(request.question, history)

    state.last_result = result["answer"]
    state.conversation.append({"role": "assistant", "content": result["answer"]})

    response = {
        "answer": result["answer"],
        "source": "Gemini Agent",
        # Pass the answer + full history so suggestions build on what
        # was just asked and answered instead of only the raw question.
        "suggestions": generate_suggestions(request.question, result["answer"], state.conversation),
        "charts": result["charts"],
    }

    # Backwards-compat single-chart shape for the current frontend
    # (ChatInput.jsx checks response.data.type === "chart").
    if result["charts"]:
        response["type"] = "chart"
        response["image"] = result["charts"][0]["image"]

    return response


@router.delete("/chat")
def clear_chat():
    state.conversation.clear()
    state.last_question = ""
    state.last_result = None

    return {"message": "Conversation cleared."}
