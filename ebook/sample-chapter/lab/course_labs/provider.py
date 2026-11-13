"""Explicit, free-only OpenRouter access. Offline fixtures live in the examples."""

import os
from decimal import Decimal, InvalidOperation
from functools import lru_cache

import httpx
from dotenv import load_dotenv

from .common import ROOT

BASE = "https://openrouter.ai/api/v1"


def is_free_tool_model(item):
    try:
        prices = item.get("pricing", {})
        return (
            item["id"].endswith(":free")
            and all(Decimal(str(prices.get(k, "-1"))) == 0 for k in ("prompt", "completion"))
            and {"tools", "tool_choice"}.issubset(item.get("supported_parameters") or [])
        )
    except (KeyError, InvalidOperation):
        return False


@lru_cache(maxsize=1)
def catalog():
    with httpx.Client(timeout=20) as client:
        response = client.get(BASE + "/models")
        response.raise_for_status()
        return response.json()["data"]


def complete(messages, tools=None):
    load_dotenv(ROOT / ".env", override=False)
    key, model = os.getenv("OPENROUTER_API_KEY", ""), os.getenv("OPENROUTER_MODEL", "")
    if not key or not model:
        raise ValueError("Set your own OPENROUTER_API_KEY and OPENROUTER_MODEL in .env; see setup/README.md")
    selected = next((item for item in catalog() if item["id"] == model and is_free_tool_model(item)), None)
    if selected is None:
        raise ValueError("Selected model must be a currently listed, zero-priced :free tool model")
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1200,
        "provider": {"allow_fallbacks": False, "require_parameters": True},
    }
    if "reasoning" in selected.get("supported_parameters", []) and not selected.get("reasoning", {}).get(
        "mandatory", False
    ):
        payload["reasoning"] = {"enabled": False, "exclude": True}
    if tools:
        payload.update(tools=tools, tool_choice="auto")
    try:
        with httpx.Client(timeout=45) as client:
            response = client.post(
                BASE + "/chat/completions", headers={"Authorization": "Bearer " + key}, json=payload
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError:
        raise RuntimeError(
            "Live provider request failed or timed out. No offline or paid fallback was used."
        ) from None
    choices = result.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    if not message.get("tool_calls") and not (message.get("content") or "").strip():
        reason = (
            "response budget reached"
            if choices and choices[0].get("finish_reason") == "length"
            else "empty response"
        )
        raise RuntimeError(
            f"Live provider returned no usable answer/tool request ({reason}). Choose a suitable model; no fallback was used."
        )
    if choices[0].get("finish_reason") == "length":
        raise RuntimeError(
            "Live model response was truncated by the output budget; no complete answer was accepted and no fallback was used."
        )
    return message, result.get("usage", {})
