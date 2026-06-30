"""
tools.py
--------
Defines the three tools the agent can call:
1. calculator  -> evaluates a math expression safely
2. web_search  -> searches the web using DuckDuckGo (no API key required)
3. get_weather -> fetches current weather using wttr.in (no API key required)

Each tool is a plain Python function PLUS a JSON-schema description that we
hand to the LLM so it knows when and how to call it (OpenAI "function calling").
"""

import ast
import operator
import requests


# ---------------------------------------------------------------------------
# 1. CALCULATOR TOOL
# ---------------------------------------------------------------------------
# We do NOT use eval() because eval() can execute arbitrary code and is a
# security risk. Instead we walk a parsed AST and only allow safe math ops.

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):  # numbers
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator {op_type} not allowed")
        return _ALLOWED_OPERATORS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator {op_type} not allowed")
        return _ALLOWED_OPERATORS[op_type](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {node}")


def calculator(expression: str) -> str:
    """Safely evaluate a math expression like '12 * (3 + 4) / 2'."""
    try:
        parsed = ast.parse(expression, mode="eval").body
        result = _safe_eval(parsed)
        return str(result)
    except Exception as exc:  # noqa: BLE001
        return f"Error evaluating expression: {exc}"


# ---------------------------------------------------------------------------
# 2. WEB SEARCH TOOL  (DuckDuckGo via the `ddgs` package — free, no API key)
# ---------------------------------------------------------------------------
def web_search(query: str, max_results: int = 4) -> str:
    """Search the web for a query and return a short summary of top results."""
    try:
        try:
            from ddgs import DDGS  # new package name
        except ImportError:
            from duckduckgo_search import DDGS  # fallback to old name

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- {r.get('title')}: {r.get('body')} ({r.get('href')})")

        if not results:
            return "No search results found."
        return "\n".join(results)
    except Exception as exc:  # noqa: BLE001
        return f"Error performing search: {exc}"


# ---------------------------------------------------------------------------
# 3. WEATHER TOOL  (Open-Meteo — free, no API key needed, very reliable)
# ---------------------------------------------------------------------------
_WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def get_weather(city: str) -> str:
    """Get current weather for a city using Open-Meteo's free geocoding + forecast API."""
    try:
        # Step 1: geocode the city name to lat/lon
        geo_resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10,
        )
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return f"Could not find location '{city}'."

        place = geo_data["results"][0]
        lat, lon = place["latitude"], place["longitude"]
        resolved_name = f"{place['name']}, {place.get('country', '')}"

        # Step 2: fetch current weather for those coordinates
        weather_resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            },
            timeout=10,
        )
        weather_resp.raise_for_status()
        current = weather_resp.json()["current"]

        desc = _WEATHER_CODES.get(current["weather_code"], "Unknown conditions")
        return (
            f"Weather in {resolved_name}: {desc}, {current['temperature_2m']}°C, "
            f"humidity {current['relative_humidity_2m']}%, "
            f"wind {current['wind_speed_10m']} km/h."
        )
    except Exception as exc:  # noqa: BLE001
        return f"Error fetching weather for {city}: {exc}"


# ---------------------------------------------------------------------------
# OpenAI function-calling schemas
# ---------------------------------------------------------------------------
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression and return the numeric result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A math expression, e.g. '(25 * 4) - 10 / 2'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for up-to-date information on a topic and return summarized results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather conditions for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Rawalpindi' or 'London'",
                    }
                },
                "required": ["city"],
            },
        },
    },
]

# Maps tool name -> actual python function, used by the agent to execute calls
TOOL_REGISTRY = {
    "calculator": calculator,
    "web_search": web_search,
    "get_weather": get_weather,
}
