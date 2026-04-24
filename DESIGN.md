# 🏗️ System Design

## 🎯 Objective

Build a tool-augmented LLM agent that:

- Chooses the correct data source
- Combines multiple sources when needed
- Produces grounded, cited answers
- Logs reasoning steps for evaluation

---

## 🧠 Architecture Overview

User Query
↓
Agent Loop (LLM)
↓
Tool Selection
↓
Tool Execution
↓
Result → LLM
↓
Final Answer + Citations
↓
Trace Logging


---

## 🧩 Components

### 1. Agent Loop (`agent_loop.py`)

- Controls execution flow
- Uses OpenRouter LLM
- Supports up to 8 reasoning steps
- Handles tool calls dynamically

---

### 2. Tools

#### 📄 search_docs (RAG)

- Embedding model: all-MiniLM-L6-v2
- Vector DB: FAISS
- Splitting: 500 chars + overlap
- Use case: opinions, themes, reviews

---

#### 📊 query_data (Structured)

- Engine: pandas
- Matching: regex + rapidfuzz
- Handles:
  - aggregation (max, avg)
  - filtering
  - comparisons

---

#### 🌐 web_search

- Primary: Tavily API
- Fallback: DuckDuckGo
- Use case: recent events

---

### 3. Prompt Design (`prompts.py`)

Defines:

- Tool selection rules
- Citation requirements
- Stop conditions
- Hallucination prevention

---

### 4. Utilities (`utils.py`)

Handles:

- Trace creation
- Step logging
- Citation extraction
- Output formatting

---

## 🔁 Agent Workflow

1. LLM receives question + tools
2. Chooses tool via function calling
3. Tool executes and returns structured output
4. Result appended to conversation
5. Loop continues until:
   - answer is complete OR
   - step limit reached

---

## 🧠 Tool Contract Design

Each tool is designed with a clear contract so that the LLM can reliably call it:

- search_docs(query: str)
- query_data(question: str)
- web_search(query: str)

Why this matters:
- Reduces ambiguity in tool usage
- Improves reliability of LLM decisions
- Prevents malformed tool calls

---

## 🤖 Tool Selection Strategy

The LLM selects tools using function-calling based on:

- Query intent (numeric vs descriptive vs recent)
- Tool descriptions provided in prompt

Example:
- "highest gross movie" → query_data
- "themes of parasite" → search_docs
- "oscar winners 2024" → web_search

---

## ⚖️ Design Trade-offs

### 1. Rule-based vs LLM-based structured querying

Chosen: Hybrid (regex + fuzzy)

Why:
- Pure LLM → unreliable for numbers
- Pure rules → too rigid
- Hybrid → balance of flexibility and accuracy

---

### 2. Local RAG vs external APIs

Chosen: Local FAISS

Why:
- Fast
- No API cost
- Deterministic

Trade-off:
- Limited dataset size


## 📌 Design Decisions

### Why multiple tools?

Different data types require different processing:

| Type | Tool |
|------|-----|
| Text | RAG |
| Numbers | pandas |
| Live | web |

---

### Why hybrid query_data?

- Regex → structured logic
- Fuzzy → robustness

---

### Why step limit?

Prevents:
- infinite loops
- excessive cost

---

### Why trace system?

- Debugging
- Evaluation transparency
- Failure analysis

---

## 🚀 Extensibility

- Replace FAISS with Pinecone
- Add more tools (e.g., recommendation engine)
- Improve intent detection with LLM parsing
