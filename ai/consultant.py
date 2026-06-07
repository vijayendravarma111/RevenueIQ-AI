import google.generativeai as genai

from ai.prompts import SYSTEM_PROMPT

def get_response(
    api_key,
    context,
    question
):

    genai.configure(
        api_key=api_key
    )

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    prompt = f"""
{SYSTEM_PROMPT}

BUSINESS DATA:

{context}

QUESTION:

{question}
"""

    response = model.generate_content(
        prompt
    )

    return response.text