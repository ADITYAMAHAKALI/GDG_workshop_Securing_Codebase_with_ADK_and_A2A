# # utils/gitingestion.py
# from __future__ import annotations
# from dataclasses import dataclass
# from typing import Dict, Any
# import asyncio
# import concurrent.futures
# from gitingest import ingest, ingest_async
# from utils.logger_config import setup_logger

# logger = setup_logger("Gitingest")

# @dataclass
# class RepoDigest:
#     repo_url: str
#     summary: str
#     tree: str
#     content: str

#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "repo_url": self.repo_url,
#             "summary": self.summary,
#             "tree": self.tree,
#             "content": self.content,
#         }

# async def _ingest_async(repo_url: str) -> RepoDigest:
#     """Async version — safe for uvicorn and orchestrator contexts."""
#     logger.info(f"Starting async ingest for repo: {repo_url}")
#     try:
#         # Prefer async API if supported
#         if callable(ingest_async):
#             summary, tree, content = await ingest_async(repo_url)
#         else:
#             # Fallback to thread-based sync ingest
#             loop = asyncio.get_running_loop()
#             with concurrent.futures.ThreadPoolExecutor() as pool:
#                 summary, tree, content = await loop.run_in_executor(pool, ingest, repo_url)
#         logger.info(f"✅ Ingest complete — summary length {len(summary)} chars")
#         return RepoDigest(repo_url=repo_url, summary=summary, tree=tree, content=content)
#     except Exception as e:
#         logger.error(f"❌ Ingest failed: {e}")
#         raise

# def gitingest_repo(repo_url: str) -> RepoDigest:
#     """
#     Wrapper safe for both sync and async environments (Uvicorn/ADK included).
#     Runs blocking ingest in executor if already in an event loop.
#     """
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = None

#     # Running inside ADK / uvicorn → use executor
#     if loop and loop.is_running():
#         logger.info("Detected existing event loop — using executor for ingest()")
#         with concurrent.futures.ThreadPoolExecutor() as pool:
#             future = loop.run_in_executor(pool, ingest, repo_url)
#             summary, tree, content = loop.run_until_complete(future)
#             return RepoDigest(repo_url=repo_url, summary=summary, tree=tree, content=content)

#     # Standalone mode
#     logger.info("Running outside event loop — using asyncio.run() for ingest_async()")
#     return asyncio.run(_ingest_async(repo_url))

# utils/gitingestion.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import asyncio
import concurrent.futures
from gitingest import ingest, ingest_async
from utils.logger_config import setup_logger
import os
from dotenv import load_dotenv
load_dotenv()
github_token = os.getenv("GITHUB_TOKEN",None)
    

logger = setup_logger("Gitingest")

@dataclass
class RepoDigest:
    repo_url: str
    summary: str
    tree: str
    content: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_url": self.repo_url,
            "summary": self.summary,
            "tree": self.tree,
            "content": self.content,
        }

async def _ingest_async(repo_url: str) -> RepoDigest:
    """Async version — safe for uvicorn/ADK loops."""
    logger.info(f"Starting async ingest for repo: {repo_url}")
    try:
        if callable(ingest_async):
            summary, tree, content = await ingest_async(repo_url)
        else:
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                summary, tree, content = await loop.run_in_executor(pool, ingest, repo_url)
        logger.info(f"✅ Ingest complete — summary length {len(summary)} chars")
        return RepoDigest(repo_url=repo_url, summary=summary, tree=tree, content=content)
    except Exception as e:
        logger.error(f"❌ Ingest failed: {e}")
        raise

def gitingest_repo(repo_url: str) -> RepoDigest:
    """
    Safe for both sync and async ADK contexts.
    If already in an async loop (e.g., uvicorn), off-load ingest() to a background thread.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    # Inside ADK / Uvicorn event loop → use thread off-load
    if loop and loop.is_running():
        logger.info("Detected existing async loop — off-loading ingest() to background thread.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(ingest, repo_url)
            summary, tree, content = future.result()
        return RepoDigest(repo_url=repo_url, summary=summary, tree=tree, content=content)

    # Stand-alone / CLI mode
    logger.info("No event loop detected — running _ingest_async() normally.")
    return asyncio.run(_ingest_async(repo_url))


if __name__ == "__main__":
    test_repo = "https://github.com/ADITYAMAHAKALI/gdg-vuln-sample-repo"
    digest = gitingest_repo(test_repo)
    print(f"\nSummary snippet:\n{digest.summary[:500]}")
    print(f"\nTree:\n{digest.tree}")
