# AlgoHub Task 1 — Intro to AI Agents & Tool Use

**Week 1 Project | AlgoHub AI Agents & Automation Internship**

An AI agent that uses **OpenAI function calling** to decide, on its own, when to call one
of three tools — a **calculator**, a **web search** tool, and a **weather** tool — to
answer a user's question. Built with a custom agent loop (no framework dependency yet;
LangChain's agent abstractions are introduced starting Week 2) and deployed as a
**Streamlit** chat app.

---

## 1. Project Overview

| | |
|---|---|
| **Objective** | Build a first agent that uses tools via function calling |
| **Concepts covered** | Agent loop basics, function/tool calling, tool registration |
| **Tools implemented** | Calculator, Web Search (DuckDuckGo), Weather (Open-Meteo) |
| **LLM** | OpenAI `gpt-4o-mini` (configurable to `gpt-4o`) |
| **Deployment** | Streamlit app |

## 2. How the Agent Works (Agent Loop)

1. The user sends a message (e.g. *"What's the weather in Lahore and what's 23% of 540?"*).
2. The message + tool schemas are sent to the LLM.
3. If the LLM decides a tool is needed, it returns a structured tool call instead of text.
4. The app executes the matching Python function (`tools.py`) and feeds the result back
   to the LLM.
5. Steps 3–4 repeat until the LLM has enough information to answer in plain language.
6. The final answer — plus the full reasoning trace (action → observation) — is shown
   in the Streamlit UI.

This Reason → Act → Observe cycle is the foundation that the **ReAct agent in Week 2**
builds on.

## 3. Folder Structure

```
AlgoHub_Task1_AIAgentToolUse/
├── app.py              # Streamlit UI (chat interface)
├── agent.py            # Agent loop / function-calling orchestration
├── tools.py            # Tool implementations + JSON schemas
├── test_tools.py        # Unit tests for the calculator tool
├── requirements.txt     # Python dependencies
├── .env.example          # Template for your OpenAI API key
├── README.md             # This file
└── screenshots/           # Demo screenshots (add your own before submission)
```

## 4. Dataset Information

This project does not use a static dataset — it relies on **live data** fetched at
query time:
- Weather data comes from the [Open-Meteo](https://open-meteo.com/) free public API
  (no key required).
- Search results come from DuckDuckGo via the `ddgs` Python package (no key required).
- Math expressions are evaluated locally with a safe AST-based parser (no external call).

No dataset request was made to AlgoHub, in line with the program's dataset policy —
all sources above were independently researched and selected as free, keyless,
beginner-friendly APIs suitable for an agent demo.

## 5. Installation Guide

```bash
# 1. Clone your fork of the repo
git clone https://github.com/<your-username>/AlgoHub_Task1_AIAgentToolUse.git
cd AlgoHub_Task1_AIAgentToolUse

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenAI API key
cp .env.example .env
# then edit .env and paste your key
# (alternatively, paste it directly into the Streamlit sidebar at runtime)

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## 6. Running Tests

```bash
pytest test_tools.py -v
```

## 7. Example Usage

| You ask | Agent does |
|---|---|
| "What's (45*12) - 89/4?" | Calls `calculator`, returns `517.75` |
| "What's the weather in Rawalpindi?" | Calls `get_weather`, returns live conditions |
| "Search for the latest LangChain release notes" | Calls `web_search`, summarizes top results |
| "If it's above 30°C in Karachi, suggest an indoor activity" | Calls `get_weather`, then reasons over the result |

## 8. Results & Screenshots

> Add 2–4 screenshots here before submission, showing:
> 1. The calculator tool being triggered
> 2. The weather tool being triggered
> 3. The web search tool being triggered
> 4. The full reasoning trace expanded in the UI

`![calculator demo](screenshots/calculator_demo.png)`
`![weather demo](screenshots/weather_demo.png)`
`![search demo](screenshots/search_demo.png)`

## 9. Deployment

Deployed as a Streamlit app. To deploy publicly:
1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub repo,
   set `app.py` as the entry point.
3. Add `OPENAI_API_KEY` under the app's **Secrets** settings instead of committing `.env`.
4. Copy the live URL into your submission along with the GitHub repo and demo video.

## 10. Notes on Security

- The calculator tool uses Python's `ast` module to parse expressions and only
  evaluates whitelisted operators (`+ - * / ** %`) — it deliberately avoids `eval()`
  to prevent arbitrary code execution.
- No API keys are hard-coded; the key is read from `.env` or entered at runtime in the
  Streamlit sidebar and is never persisted to disk by the app.

---
**AlgoHub Software House | Week 1 Submission**
