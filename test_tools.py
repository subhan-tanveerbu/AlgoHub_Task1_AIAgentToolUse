"""
test_tools.py
-------------
Basic sanity tests for the three tools. Run with:
    pytest test_tools.py -v
"""

from tools import calculator


def test_calculator_basic():
    assert calculator("2 + 2") == "4"


def test_calculator_order_of_operations():
    assert calculator("(45*12)-89/4") == "517.75"


def test_calculator_rejects_unsafe_input():
    # Should fail gracefully, not execute arbitrary code
    result = calculator("__import__('os').system('echo hacked')")
    assert "Error" in result


def test_calculator_division():
    assert calculator("10 / 4") == "2.5"


# Note: web_search and get_weather are network-dependent and are best
# verified manually / via integration testing once deployed, since unit
# tests shouldn't depend on live external services.
