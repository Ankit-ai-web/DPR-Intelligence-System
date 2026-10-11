import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_dpr(text: str) -> str:
    prompt = f"""
You are an expert DPR (Detailed Project Report) intelligence analyst.

Analyze the following project document and extract structured project
intelligence.

Return ONLY valid JSON.
Do not use Markdown.
Do not use ```json or ```.

Use exactly this structure:

{{
  "executive_summary": "string",
  "project_details": {{
    "project_name": "string or Not specified in document",
    "objective": "string or Not specified in document",
    "project_type": "string or Not specified in document",
    "duration": "string or Not specified in document"
  }},
  "financials": {{
    "budget": "string or Not specified in document",
    "funding": "string or Not specified in document",
    "financial_completeness": 0
  }},
  "timeline": {{
    "start_date": "string or Not specified in document",
    "end_date": "string or Not specified in document",
    "duration": "string or Not specified in document",
    "timeline_completeness": 0
  }},
  "risks": [
    {{
      "risk": "string",
      "severity": "Low | Medium | High"
    }}
  ],
  "missing_information": [
    "string"
  ],
  "recommendations": [
    "string"
  ],
  "risk_score": 0,
  "data_completeness": 0,
  "health_score": 0,
  "risk_level": "Low | Medium | High"
}}

SCORING RULES:

risk_score:
- 0-30 = Low
- 31-60 = Medium
- 61-100 = High

health_score:
- 80-100 = Excellent
- 60-79 = Good
- 40-59 = Needs Attention
- 0-39 = Critical

data_completeness:
- Estimate how much important project information is actually
  available in the document.
- 0 means almost no useful project information.
- 100 means the important project information is comprehensive.

health_score should consider:
- availability of project information
- financial information
- timeline information
- identified risks
- missing information

IMPORTANT:
- Use ONLY information present in the document.
- Never invent numbers, dates, budgets, names, or facts.
- If information is unavailable, use "Not specified in document".
- risk_score, data_completeness, and health_score must be integers from 0 to 100.
- Keep recommendations practical and specific.
- Return valid JSON only.

DOCUMENT:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    # Validate that Gemini returned valid JSON
    try:
        parsed = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini returned invalid JSON: {e}"
        )

    # Return formatted JSON string for database storage
    return json.dumps(
        parsed,
        indent=2,
        ensure_ascii=False
    )