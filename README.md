# 🤖 AlgoHub Task 1 — Intro to AI Agents & Tool Use

**Week 1 Project | AlgoHub AI Agents & Automation Internship**

An AI agent that uses **OpenAI function calling** to intelligently decide when to use tools such as a **calculator**, **web search**, and **weather API** to answer user queries.

Built using a **custom agent loop (Reason → Act → Observe)** without external frameworks like LangChain (introduced in Week 2), and deployed as a **Streamlit chat application**.

---

## 📌 1. Project Overview

| Feature | Description |
|--------|-------------|
| 🎯 Objective | Build a tool-using AI agent using function calling |
| 🧠 Concept | Agent loop (Reason → Act → Observe) |
| 🔧 Tools | Calculator, Web Search (DuckDuckGo), Weather (Open-Meteo) |
| 🤖 LLM | OpenAI `gpt-4o-mini` (configurable to `gpt-4o`) |
| 🌐 UI | Streamlit Chat Interface |

---

## ⚙️ 2. How the Agent Works

1. User enters a query (e.g., “Weather in Lahore + 23% of 540”)
2. Query + tool schemas are sent to the LLM
3. LLM decides whether to:
   - Respond directly OR
   - Call a tool
4. Tool executes in Python (`tools.py`)
5. Result is sent back to the LLM
6. Steps repeat until final answer is generated
7. Full reasoning trace (action → observation) is shown in UI

---

## 📁 3. Project Structure


AlgoHub_Task1_AIAgentToolUse/
│
├── app.py
├── agent.py
├── tools.py
├── test_tools.py
├── requirements.txt
├── .env.example
├── README.md
└── screenshots/


---

## 🌐 4. Data Sources (No Dataset Required)

- Weather → Open-Meteo API (free, no API key)
- Web Search → DuckDuckGo (`ddgs` package)
- Calculator → Safe AST-based evaluator (local execution)

---

## 🛠️ 5. Installation Guide

```bash
git clone https://github.com/<your-username>/AlgoHub_Task1_AIAgentToolUse.git
cd AlgoHub_Task1_AIAgentToolUse

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

cp .env.example .env

streamlit run app.py
🧪 6. Running Tests
pytest test_tools.py -v
💡 7. Example Queries
Query	Tool Used
“What is (45×12) - 89/4?”	Calculator
“Weather in Rawalpindi”	Weather API
“Latest AI news”	Web Search
“If temp > 30°C, suggest activity”	Weather + Reasoning
📸 8. Screenshots








🚀 9. Deployment
Push repo to GitHub
Open https://share.streamlit.io
Select repo and app.py
Add OPENAI_API_KEY in Secrets
Deploy
🔐 10. Security Notes
No API keys committed to repo
.env excluded using .gitignore
No unsafe eval() used
Safe tool execution via AST parsing
👨‍💻 Author

AlgoHub Software House Internship
Week 1 Project — AI Agents & Tool Use
