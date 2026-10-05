import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_dpr(text: str) -> str:
    prompt = f"""
You are an expert DPR (Detailed Project Report) analyst.

Analyze the following project document and provide a professional,
structured analysis.

Return the following sections:

1. Executive Summary
2. Project Details
3. Budget / Financial Information
4. Timeline
5. Key Risks
6. Missing Information
7. Recommendations

Rules:
- Be factual.
- Use only information available in the document.
- Do not invent facts or numbers.
- If information is unavailable, write "Not specified in document".
- Keep the analysis clear and professional.
- Use headings and bullet points where appropriate.

DOCUMENT:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text