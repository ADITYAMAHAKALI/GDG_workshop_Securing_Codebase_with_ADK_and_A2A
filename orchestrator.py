# orchestrator.py
import asyncio
import argparse
import time
from uuid import uuid4
import httpx
import os
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import Message, MessageSendParams, Part, Role, SendMessageRequest, TextPart
from utils.logger_config import setup_logger
logger = setup_logger("Orchestrator")
# Persistent clients cache
_clients = {}


async def get_client_for_agent(base_url: str) -> A2AClient:
    """Fetch or reuse a cached A2AClient for an agent."""
    if base_url in _clients:
        return _clients[base_url]

    logger.info(f"[Orchestrator] 🔍 Discovering agent at {base_url}...")
    httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(180.0))
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
    agent_card = await resolver.get_agent_card()
    client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
    _clients[base_url] = client
    logger.info(f"[Orchestrator] ✅ Found agent: {agent_card.name}")
    return client


async def _send_text_message(client: A2AClient, text: str) -> str:
    """Send a simple text message and extract its first text response."""
    msg = Message(role=Role.user, messageId=str(uuid4()),
                  parts=[Part(root=TextPart(text=text))])
    req = SendMessageRequest(
        id=str(uuid4()), params=MessageSendParams(message=msg))

    for attempt in range(3):
        try:
            resp = await asyncio.wait_for(client.send_message(req), timeout=180)
            rj = resp.model_dump(mode="json", exclude_none=True)
            # Try both possible return formats
            for keypath in [
                ["result", "status", "message", "parts", 0, "text"],
                ["result", "artifacts", 0, "parts", 0, "text"],
            ]:
                data = rj
                try:
                    for k in keypath:
                        data = data[k]
                    return data
                except Exception:
                    continue
            raise RuntimeError(f"Unexpected response: {rj}")
        except Exception as e:
            logger.warn(
                f"[WARN] Retrying message send (attempt {attempt+1}/3): {e}")
            await asyncio.sleep(2 * (attempt + 1))
    raise RuntimeError("All retries failed")


async def run_scan(repo_url: str) -> str:
    """3-agent workflow with performance optimizations."""
    scanner, analyzer, reporter = await asyncio.gather(
        get_client_for_agent("http://localhost:8001"),
        get_client_for_agent("http://localhost:8002"),
        get_client_for_agent("http://localhost:8003"),
    )

    t0 = time.time()
    logger.info(f"\n[Orchestrator] 🚀 Starting scan for {repo_url}")

    # Step 1
    repo_digest = await _send_text_message(scanner, repo_url)
    logger.info(
        f"[1/3] Scanner complete ({len(repo_digest)} bytes) [{time.time()-t0:.1f}s]")

    # Step 2 + Step 3 (chained)
    vuln_json = await _send_text_message(analyzer, repo_digest)
    logger.info(
        f"[2/3] Analyzer complete ({len(vuln_json)} bytes) [{time.time()-t0:.1f}s]")

    report_md = await _send_text_message(reporter, vuln_json)
    logger.info(f"[3/3] Reporter complete [{time.time()-t0:.1f}s total]")
    return report_md


def run_scan_sync(repo_url: str) -> str:
    """Sync wrapper for Streamlit / CLI."""
    return asyncio.run(run_scan(repo_url))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="3-Agent Repo Security Scanner")
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    report = run_scan_sync(args.url)
    logger.info("\n" + "="*60 + "\nFINAL SECURITY REPORT\n" +
                "="*60 + f"\n\n{report}")
    os.makedirs("reports", exist_ok=True)
    with open("reports"+f'/{args.url.replace("://", "_").replace("/", "_") + ".md"}', "w") as f:
        f.write(report)
