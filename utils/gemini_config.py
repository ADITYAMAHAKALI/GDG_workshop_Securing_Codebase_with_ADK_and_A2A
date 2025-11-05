# utils/gemini_config.py

import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from utils.schemas import AnalysisSchema

from dotenv import load_dotenv
load_dotenv()

# Prefer GOOGLE_API_KEY (used by ADK) but fall back to GEMINI_API_KEY for flexibility
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in your environment or .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)
print("[Config] Gemini API key configured.", GEMINI_API_KEY)

VULN_ANALYSIS_SYSTEM_PROMPT = """
You are a senior application security engineer.

You will receive a structured digest of a source-code repository created
by the gitingest tool. It contains:
- A textual summary of the repo
- A directory tree
- A long "content" section with code and config snippets,
  prefixed by file names (e.g., "File: src/app.py").

Your job is to perform a best-effort security review of the ENTIRE repo.

You MUST:
1. Identify potential vulnerabilities and risky patterns in code, configs, and
   dependency usage, such as (non-exhaustive examples):
   - Dynamic code execution (eval/exec, child_process.exec, subprocess with shell=True)
   - SQL injection (string-concatenated SQL with untrusted input)
   - Command injection, path traversal, unsafe deserialization
   - Insecure HTTP/TLS (verify=False, disabled SSL verification)
   - Hardcoded secrets (API keys, tokens, private keys, passwords)
   - Insecure framework configuration (debug mode in production, overly permissive CORS)
   - Very old or obviously deprecated libraries (if clearly visible in code or manifests).

2. For each issue, produce:
   - A short identifier
   - File path (best-effort)
   - Severity (LOW, MEDIUM, HIGH, CRITICAL)
   - Category (Code, Dependency, Config, Secret, Other)
   - A brief snippet or description
   - A clear remediation recommendation.

3. Aggregate overall stats:
   - Total number of findings
   - Counts by severity
   - Counts by category.

Limitations:
- You do NOT have live CVE access. Use your training only.
- Be conservative with severity if unsure.
- If you are unsure of the file path or lines, use "unknown".

Output:
Return a single JSON object conforming EXACTLY to the RepoVulnerabilityReport
schema provided out of band. NO additional commentary or text.
"""

REPORT_FORMATTER_SYSTEM_PROMPT = """
You are a helpful assistant turning a machine-readable security report into
a readable Markdown document for developers.

Input: a JSON object with:
- repo_url
- summary
- findings[]
- stats.total, stats.by_severity, stats.by_category

Output: Markdown with sections:
- # Security Report for <repo>
- ## Overview
- ## Statistics
- ## High & Critical Findings
- ## Medium & Low Findings
- ## Recommended Next Steps

Use:
- 🚨 for CRITICAL/HIGH
- 🟡 for MEDIUM
- ✅ for informational / no issues.

Be concise and technical.
"""

JSON_GENERATION_CONFIG = GenerationConfig(
    response_mime_type="application/json",
    response_schema=AnalysisSchema,  # enforce RepoVulnerabilityReport
)

TEXT_GENERATION_CONFIG = GenerationConfig(
    response_mime_type="text/plain",
)

vuln_analysis_model = genai.GenerativeModel(
    "gemini-1.5-pro",
    system_instruction=VULN_ANALYSIS_SYSTEM_PROMPT,
    generation_config=JSON_GENERATION_CONFIG,
)

report_formatter_model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=REPORT_FORMATTER_SYSTEM_PROMPT,
    generation_config=TEXT_GENERATION_CONFIG,
)
