# agents/analyzer_agent.py

from dotenv import load_dotenv
import google.generativeai as genai
import os
from utils.logger_config import setup_logger
import uvicorn
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import sys
sys.path.append("..")
load_dotenv()

# Prefer GOOGLE_API_KEY (used by ADK) but fall back to GEMINI_API_KEY for flexibility
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in your environment or .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)


VULN_ANALYSIS_INSTRUCTION = """
You are a senior application security engineer.

Input:
- The user will provide a JSON string produced by a repo-ingest tool (a RepoDigest).
- It contains repository summary, file tree, and contents of important files
  (like app code, config, and secrets).

Task:
- Analyze the entire repo for security risks, including but not limited to:
  - Hard-coded secrets (API keys, tokens, passwords).
  - Insecure use of HTTP clients (e.g. verify=False, SSRF patterns).
  - Dangerous patterns like eval/exec, command execution, or direct SQL concatenation.
  - Insecure framework configuration (debug=true, wildcard CORS, etc.).
  - Obviously outdated or risky dependencies when visible in the digest.

Output:
- Respond ONLY with a single JSON object (no markdown, no prose).
- Use this shape (keys are required):

{
  "repo_summary": {
    "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
    "short_overview": "1-3 sentence summary of the repo and overall risk."
  },
  "findings": [
    {
      "id": "F001",
      "title": "Short title",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "file": "relative/path/to/file.py",
      "line_hint": "e.g. 'around line 42'",
      "description": "What is the issue and why it is risky.",
      "recommendation": "What the developer should do to fix or mitigate it."
    }
  ]
}

- If you find nothing, return the same shape but with an empty `findings` array
  and `risk_level` = "LOW".
- Do NOT add any extra keys or commentary outside this JSON.
"""


root_agent = Agent(
    name="analyzer_agent",
    model="gemini-2.5-pro",
    description="Analyzes a gitingest RepoDigest JSON and returns a repo-level vulnerability report JSON.",
    instruction=VULN_ANALYSIS_INSTRUCTION,
    tools=[],  # pure LLM; the "tool" is just its reasoning over the JSON
)

# Expose as A2A server
a2a_app = to_a2a(root_agent, port=8002)


if __name__ == "__main__":
    # Run with: python -m uvicorn agents.analyzer_agent:a2a_app --reload --port 8002
    uvicorn.run(a2a_app, host="0.0.0.0", port=8002)
