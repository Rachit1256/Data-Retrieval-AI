from google import genai
from dotenv import load_dotenv
import os
import state

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_gemini(context, question):

    history = "\n".join(
        [
            f"{msg['role']}: {msg['content']}"
            for msg in state.conversation[-8:]
        ]
    )

    prompt = f"""
You are an AI Spreadsheet Assistant.

========================
Conversation History
========================

{history}

========================
Spreadsheet Context
========================

{context}

========================
Current User Question
========================

{question}

Rules:

1. Answer ONLY using spreadsheet data.

2. Never make up values.

3. If information is unavailable say:
Data not found.

4. Give concise answers.

5. If comparison is requested,
compare carefully.

6. Use bullet points whenever possible.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text