"""
agent_loop.py — Minimal agent loop using OpenRouter.
"""

import os, json
from openai import OpenAI
from dotenv import load_dotenv

from tools.query_data import query_data
from tools.web_search import web_search
from tools.search_docs import search_docs
from agent.prompts import SYSTEM_PROMPT, HARD_CAP_REFUSAL
from agent.utils import new_trace, log_step, trace_to_text, save_trace, format_tool_result

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "meta-llama/llama-3-8b-instruct"
MAX_STEPS = 8

TOOLS = [
    {"type": "function", "function": {
        "name": "search_docs",
        "description": "Search local movie review documents for opinions, themes, critic analysis.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    }},
    {"type": "function", "function": {
        "name": "query_data",
        "description": "Query structured CSV for box-office numbers, budgets, RT scores, rankings.",
        "parameters": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]}
    }},
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search the live web for recent news, awards, streaming info.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    }},
]

def dispatch(name, args):
    if name == "search_docs":  return search_docs(args.get("query", ""))
    if name == "query_data":   return query_data(args.get("question") or args.get("query", ""))
    if name == "web_search":   return web_search(args.get("query", ""))
    return "error: unknown tool"

def run_agent(question):
    trace = new_trace(question)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": question}
    ]

    step = 0
    while step < MAX_STEPS:
        res = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = res.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                step += 1
                if step > MAX_STEPS:
                    break
                name = call.function.name
                args = json.loads(call.function.arguments)

                print(f"  [Step {step}] Tool: {name} | Input: {args}")

                raw    = dispatch(name, args)
                result = format_tool_result(name, raw)

                log_step(trace, step, name, args, raw)
                messages.append({
                    "role":         "tool",
                    "tool_call_id": call.id,
                    "content":      result
                })
            continue

        # Final answer
        answer = (msg.content or "").strip()
        if not answer:
            continue
        trace["final_answer"] = answer
        trace["steps_used"]   = step
        trace["status"]       = "success"
        trace_text = trace_to_text(trace)
        save_trace(trace, trace_text)
        return answer

    # Hard cap hit
    trace["final_answer"] = HARD_CAP_REFUSAL
    trace["steps_used"]   = step
    trace["status"]       = "hard_cap_hit"
    save_trace(trace, trace_to_text(trace))
    return HARD_CAP_REFUSAL


if __name__ == "__main__":
    q = input("Question: ")
    print("\nThinking...\n")
    answer = run_agent(q)
    print("\nAnswer:", answer)
