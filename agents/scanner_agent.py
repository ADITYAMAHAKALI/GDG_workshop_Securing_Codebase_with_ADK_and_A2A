# agents/scanner_agent.py

from utils.gitingestion import gitingest_repo
from utils.logger_config import setup_logger
from dotenv import load_dotenv
import google.generativeai as genai
import os
import uvicorn
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import sys
sys.path.append("..")
logger = setup_logger("ScannerAgent")

load_dotenv()

# Prefer GOOGLE_API_KEY (used by ADK) but fall back to GEMINI_API_KEY for flexibility
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in your environment or .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)

sys.path.append("..")


def scan_repo(repo_url: str) -> dict:
    logger.info(f"Starting repo scan: {repo_url}")
    try:
        digest = gitingest_repo(repo_url)
        result = digest.to_dict()
        logger.info(
            f"Repo scan successful — {len(result['content'])} chars ingested.")
        return result
    except Exception as e:
        logger.error(f"Repo scan failed: {e}")
        raise


# ADK root agent: LLM + function tool
root_agent = Agent(
    name="scanner_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent that ingests a GitHub repository using gitingest and returns "
        "a JSON RepoDigest (summary, file tree, important files)."
    ),
    instruction=(
        "The user will always provide a Git repository URL as plain text.\n"
        "You MUST always call the `scan_repo` tool exactly once with that URL.\n"
        "Return ONLY the JSON object returned by `scan_repo` as your final answer.\n"
        "Do not add any extra prose, markdown, or explanation."
    ),
    tools=[scan_repo],
)

# Expose this ADK agent as an A2A-compatible ASGI app
a2a_app = to_a2a(root_agent, port=8001)


if __name__ == "__main__":
    # Run with: python -m uvicorn agents.scanner_agent:a2a_app --reload --port 8001
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
