# agents/reporter_agent.py

import uvicorn
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import os
import google.generativeai as genai
import sys
sys.path.append("..")
from utils.logger_config import setup_logger
from dotenv import load_dotenv
load_dotenv()
logger = setup_logger("ReporterAgent")

# Prefer GOOGLE_API_KEY (used by ADK) but fall back to GEMINI_API_KEY for flexibility
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in your environment or .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)


REPORT_FORMATTER_INSTRUCTION = """
You are a security report writer.

Input:
- A JSON object produced by a vulnerability analysis agent.
- It has a `repo_summary` and a list of `findings` (id, title, severity, file, description, recommendation).

Task:
- Convert this JSON into a clear, concise Markdown report for developers.

Formatting rules:
- Start with a top-level title: "# Security Report"
- Then show a short summary section:
  - Overall risk level with an emoji:
    - CRITICAL/HIGH -> 🚨
    - MEDIUM -> 🟡
    - LOW -> ✅
  - The `short_overview` text
- Then a "Findings" section:
  - If there are no findings, say "No issues detected."
  - Otherwise, for each finding:
    - Use a "##" heading with "[<id>] <title>"
    - Show severity with emojis as above
    - Show the file + line_hint on one line
    - Then bullet points for:
      - Description
      - Recommendation

Output:
- Respond ONLY with valid Markdown.
- No extra explanations outside the report.
"""


root_agent = Agent(
    name="reporter_agent",
    model="gemini-2.0-flash",
    description="Formats a repo vulnerability JSON into a developer-friendly Markdown report.",
    instruction=REPORT_FORMATTER_INSTRUCTION,
    tools=[],
)

a2a_app = to_a2a(root_agent, port=8003)


if __name__ == "__main__":
    # Run with: python -m uvicorn agents.reporter_agent:a2a_app --reload --port 8003
    uvicorn.run(a2a_app, host="0.0.0.0", port=8003)
