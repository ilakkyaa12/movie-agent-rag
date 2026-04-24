"""
utils.py — Shared utility functions for the Movie Agent.

These helpers keep agent_loop.py clean. They handle:
  - Trace creation and formatting
  - Saving traces to disk
  - Formatting tool outputs into readable strings for the LLM
"""

import os
import json
import datetime
from typing import Any


# ── Trace helpers ──────────────────────────────────────────────────────────────

def new_trace(question: str) -> dict:
    """Create a fresh trace dict for a new agent run."""
    return {
        "question":     question,
        "steps":        [],          # list of {step, tool, input, output}
        "final_answer": None,
        "citations":    [],
        "steps_used":   0,
        "timestamp":    datetime.datetime.now().isoformat(),
        "status":       "in_progress",  # success | hard_cap_hit | error
    }


def log_step(trace: dict, step_num: int, tool: str, tool_input: dict, tool_output: Any) -> None:
    """Append one tool-call step to the trace."""
    trace["steps"].append({
        "step":   step_num,
        "tool":   tool,
        "input":  tool_input,
        "output": tool_output,
    })


def trace_to_text(trace: dict, max_steps: int = 8) -> str:
    """
    Render a trace in the exact format required by the assignment spec:

        Question: <question>
        Step 1: tool=search_docs input='...'
          result=...
        Final Answer: ...
        Citations: ...
        Steps used: X / 8 max
    """
    lines = [f"Question: {trace['question']}"]

    for s in trace["steps"]:
        input_str = json.dumps(s["input"])
        lines.append(f"\nStep {s['step']}: tool={s['tool']} input={input_str}")
        raw = json.dumps(s["output"], default=str)
        # Truncate very long outputs so the trace stays readable
        display = raw[:600] + " ..." if len(raw) > 600 else raw
        lines.append(f"  result={display}")

    lines.append(f"\nFinal Answer: {trace.get('final_answer', '[none]')}")
    citations = trace.get("citations") or []
    lines.append(f"Citations: {', '.join(citations) if citations else 'none recorded'}")
    lines.append(f"Steps used: {trace['steps_used']} / {max_steps} max")
    lines.append(f"Status: {trace['status']}")
    return "\n".join(lines)


def save_trace(trace: dict, trace_text: str, log_dir: str = None) -> None:
    """Write trace to logs/traces/ as both .json and .txt."""
    if log_dir is None:
        log_dir = os.path.join(
            os.path.dirname(__file__), "..", "logs", "traces"
        )
    os.makedirs(log_dir, exist_ok=True)

    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = trace["question"][:40].replace(" ", "_").replace("/", "-")
    base = os.path.join(log_dir, f"{ts}_{slug}")

    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, default=str)

    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(trace_text)


# ── Tool output formatters ─────────────────────────────────────────────────────

def format_search_docs_result(raw: Any) -> str:
    if not raw:
        return "[search_docs returned no results]"
    if isinstance(raw, str):
        return raw
    lines = ["Document search results:"]
    for i, chunk in enumerate(raw, 1):
        source = chunk.get("source", "unknown")
        text   = chunk.get("content", chunk.get("text", ""))
        lines.append(f"\n[{i}] Source: {source}\n{text}")
    return "\n".join(lines)


def format_query_data_result(raw: Any) -> str:
    """
    Convert query_data output into a string the LLM can read.
    Expected raw format: dict with keys 'result', 'rows', 'source', 'error'.
    """
    if not isinstance(raw, dict):
        return str(raw)
    if raw.get("error"):
        return f"[query_data error: {raw['error']}]"
    result = raw.get("result", "")
    source = raw.get("source", "movies.csv")
    return f"Structured data result ({source}):\n{result}"


def format_web_search_result(raw: Any) -> str:
    if not isinstance(raw, dict) or not raw.get("results"):
        return f"[web_search returned no results. Error: {raw.get('error')}]"
    lines = [f"Web search results for: \"{raw['query']}\""]
    for i, r in enumerate(raw["results"], 1):
        lines.append(
            f"\n[{i}] {r.get('title', '')}"
            f"\n    URL      : {r.get('url', '')}"
            f"\n    Published: {r.get('published_date', 'unknown')}"
            f"\n    Snippet  : {r.get('snippet', '')}"
        )
    return "\n".join(lines)


def format_tool_result(tool_name: str, raw: Any) -> str:
    """Route to the right formatter based on tool name."""
    if tool_name == "search_docs":
        return format_search_docs_result(raw)
    elif tool_name == "query_data":
        return format_query_data_result(raw)
    elif tool_name == "web_search":
        return format_web_search_result(raw)
    return json.dumps(raw, default=str, indent=2)