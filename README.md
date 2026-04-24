# 🎬 Movie Agent RAG System

A multi-tool LLM agent that answers movie-related questions by combining:

- 📄 Unstructured data (movie reviews)
- 📊 Structured data (CSV dataset)
- 🌐 Real-time web search

The system uses a tool-calling LLM to dynamically decide which source to use and produces answers with citations.

---

## 🚀 Features

- ✅ Tool-based architecture (not a single monolithic model)
- ✅ Semantic search over movie reviews (RAG)
- ✅ Structured querying using pandas
- ✅ Live web search for recent information
- ✅ Multi-step reasoning with an agent loop
- ✅ Transparent execution with trace logging
- ✅ Citation-aware responses

---

## 🧠 How It Works

1. User asks a question
2. LLM decides which tool to use:
   - `search_docs` → reviews / opinions
   - `query_data` → numbers / facts
   - `web_search` → recent info
3. Tool executes and returns result
4. LLM may call additional tools
5. Final answer is generated with citations
6. Full trace is saved for evaluation

---

## ⚙️ Setup

 1. Create virtual environment

python -m venv venv
venv\Scripts\activate

2. Install dependencies

pip install -r requirements.txt

3. Add API keys

Create .env file:

OPENROUTER_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here


▶️ Run the Agent
python -m agent.agent_loop

📊 Tools Overview

| Tool        | Purpose              | Data Source    |
| ----------- | -------------------- | -------------- |
| search_docs | Reviews, themes      | Text documents |
| query_data  | Numbers, comparisons | CSV            |
| web_search  | Recent info          | Internet       |

