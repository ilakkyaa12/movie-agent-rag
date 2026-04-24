"""
web_search.py — Live web search tool for the Movie Agent.

Use this tool ONLY for recent information not in the local corpus —
current award results, streaming news, this week's box office, upcoming releases.
Do NOT use for questions answerable from local reviews or the movies CSV.

Primary  : Tavily  (set TAVILY_API_KEY in .env)
Fallback : DuckDuckGo (no key needed, automatic if Tavily key is missing)
"""

from __future__ import annotations
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def web_search(query: str, max_results: int = 3) -> dict:
    query = query.strip()
    if not query:
        return {"results": [], "query": query, "source": "none", "error": "Empty query."}

    # ── Try Tavily first ───────────────────────────────────────────────────────
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key:
        try:
            from tavily import TavilyClient
            client   = TavilyClient(api_key=tavily_key)
            response = client.search(query=query, max_results=max_results, search_depth="basic")
            results  = [
                {
                    "title":          r.get("title", ""),
                    "url":            r.get("url", ""),
                    "snippet":        r.get("content", ""),
                    "published_date": r.get("published_date", "unknown"),
                }
                for r in response.get("results", [])[:max_results]
            ]
            if results:
                logger.info("web_search: tavily returned %d results", len(results))
                return {"results": results, "query": query, "source": "tavily", "error": None}
        except Exception as e:
            logger.warning("Tavily failed: %s — falling back to DuckDuckGo", e)

    # ── Fallback: DuckDuckGo ───────────────────────────────────────────────────
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title":          r.get("title", ""),
                    "url":            r.get("href", ""),
                    "snippet":        r.get("body", ""),
                    "published_date": "unknown",
                })
        time.sleep(0.5)   # avoid rate-limiting
        if results:
            logger.info("web_search: duckduckgo returned %d results", len(results))
            return {"results": results, "query": query, "source": "duckduckgo", "error": None}
    except Exception as e:
        logger.error("DuckDuckGo also failed: %s", e)

    return {"results": [], "query": query, "source": "none", "error": "All search backends failed."}


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json, sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Oppenheimer Oscar wins 2024"
    out   = web_search(query)
    print(json.dumps(out, indent=2))