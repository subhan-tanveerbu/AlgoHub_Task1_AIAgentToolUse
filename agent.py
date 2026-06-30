"""
agent.py
--------
Core agent loop. Implements OpenAI "function calling" (a.k.a. tool use):

1. Send the user's message + tool schemas to the LLM.
2. If the LLM responds with a tool call, execute the matching Python
   function from tools.TOOL_REGISTRY.
3. Send the tool's result back to the LLM so it can produce a final
   natural-language answer (looping until no more tool calls are requested).

This is the "Agent Loop Basics" concept from Week 1 of the roadmap.
"""

import json
import os
from openai import OpenAI

from tools import TOOL_SCHEMAS, TOOL_REGISTRY

SYSTEM_PROMPT = """You are Aida, a helpful AI assistant with access to tools:
- calculator: for any math computation
- web_search: for current events, facts, or anything you're unsure about
- get_weather: for current weather conditions in a city

Always use a tool when it would give a more accurate or up-to-date answer
instead of guessing. After getting tool results, give a clear, concise,
friendly final answer to the user."""


class ToolAgent:
    def __init__(
        self,
        api_key: str | None = None,
        model="llama-3.3-70b-versatile"
):
        self.client = OpenAI(
            api_key=api_key or os.environ.get("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
)
        self.model = model

    def run(self, user_message: str, history: list[dict] | None = None, max_steps: int = 5):
        """
        Run the agent loop for one user message.
        Returns: (final_answer: str, trace: list[dict]) where trace logs each
        thought/action/observation step for transparency in the UI.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        trace = []

        for step in range(max_steps):
            print("MODEL BEING USED:", self.model)
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                )

            except Exception as e:
                print("Tool calling failed:", e)

                if "weather" in user_message.lower():
                    result = TOOL_REGISTRY["get_weather"]("Islamabad")
                    return result, trace

                elif "search" in user_message.lower():
                    result = TOOL_REGISTRY["web_search"](user_message)
                    return result, trace

                elif any(op in user_message for op in "+-*/%"):
                    result = TOOL_REGISTRY["calculator"](user_message)
                    return result, trace

                return f"Error: {e}", trace
                return f"Model error: {e}", trace
            msg = response.choices[0].message

            # No tool call -> final answer reached
            if not msg.tool_calls:
                trace.append({"type": "final_answer", "content": msg.content})
                return msg.content, trace

            # Append the assistant's tool-call message to history
            messages.append(msg)

            # Execute each requested tool call
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                trace.append({"type": "action", "tool": name, "input": args})

                tool_fn = TOOL_REGISTRY.get(name)
                if tool_fn is None:
                    result = f"Error: unknown tool '{name}'"
                else:
                    result = tool_fn(**args)

                trace.append({"type": "observation", "tool": name, "output": result})

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    }
                )

        # Safety net if the loop exceeds max_steps
        return "I wasn't able to finish within the allowed number of steps.", trace
