"""
app.py
------
Streamlit front-end for the Week 1 AI Agent: "First Agent with Tool Use".

Run with:
    streamlit run app.py
"""

import streamlit as st
from agent import ToolAgent

st.set_page_config(page_title="AlgoHub Agent - Week 1", page_icon="🤖", layout="centered")

st.title("🤖 AI Agent with Tool Use")
st.caption(
    "An AI agent that can calculate, search the web, and check the weather using tool calling."
)

# --- Sidebar: API key + settings -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Groq API Key", type="password", help="Your key is only used for this session.")
    model = st.selectbox(
    "Model",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ],
    index=0,
)
    show_trace = st.checkbox("Show agent reasoning trace", value=True)
    st.markdown("---")
    st.markdown("**Available tools**")
    st.markdown("- 🧮 Calculator\n- 🔎 Web Search (DuckDuckGo)\n- ⛅ Weather (wttr.in)")
    st.markdown("---")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

# --- Session state -----------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # for display
if "history" not in st.session_state:
    st.session_state.history = []  # for the LLM (role/content only)

# --- Render past messages -----------------------------------------------------------
# --- Render past messages -----------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("trace") and show_trace:
            with st.expander("🔍 Agent reasoning trace"):
                for step in msg["trace"]:
                    if step["type"] == "action":
                        st.markdown(f"**Action:** `{step['tool']}({step['input']})`")
                    elif step["type"] == "observation":
                        st.markdown(f"**Observation:** {step['output']}")
                    elif step["type"] == "final_answer":
                        st.markdown(f"**Final Answer:** {step['content']}")

# --- Chat input -----------------------------------------------------------------
user_input = st.chat_input("Ask me to calculate something, search the web, or check the weather...")

if user_input:
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            agent = ToolAgent(api_key=api_key, model=model)
            answer, trace = agent.run(user_input, history=st.session_state.history)
            st.markdown(answer)
            if show_trace:
                with st.expander("🔍 Agent reasoning trace"):
                    for step in trace:
                        if step["type"] == "action":
                            st.markdown(f"**Action:** `{step['tool']}({step['input']})`")
                        elif step["type"] == "observation":
                            st.markdown(f"**Observation:** {step['output']}")
                        elif step["type"] == "final_answer":
                            st.markdown(f"**Final Answer:** {step['content']}")

    st.session_state.messages.append({"role": "assistant", "content": answer, "trace": trace})
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": answer})

# --- Example prompts -----------------------------------------------------------------
st.markdown("---")
st.markdown("**Try asking:**")
cols = st.columns(3)
examples = [
    "What's (45 * 12) - 89 / 4?",
    "What's the weather in Rawalpindi right now?",
    "Search for the latest news on AI agents",
]
for col, example in zip(cols, examples):
    col.button(example, use_container_width=True, disabled=True, help="Type this into the chat box above")
