# utils/schemas.py

import typing


class RepoFinding(typing.TypedDict):
    """A single security finding anywhere in the repo."""
    id: str                     # e.g. "F-001"
    title: str                  # "Hardcoded secret in config.py"
    severity: str               # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    category: str               # "Code" | "Dependency" | "Config" | "Secret" | "Other"
    file_path: str              # "src/app/main.py"
    line_range: str             # "120-140" (best-effort, can be "unknown")
    snippet: str                # short snippet or description
    recommendation: str         # actionable remediation guidance


class Stats(typing.TypedDict):
    total: int
    by_severity: typing.Dict[str, int]
    by_category: typing.Dict[str, int]

class RepoVulnerabilityReport(typing.TypedDict):
    """Top-level vulnerability report for a repo."""
    repo_url: str
    summary: str                # high-level summary from gitingest
    findings: list[RepoFinding]
    stats: Stats


# JSON schema the analyzer will output:
AnalysisSchema = RepoVulnerabilityReport
