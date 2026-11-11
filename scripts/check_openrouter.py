"""Check a free model's tool-call exchange using synthetic service data."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request


BASE_URL = "https://openrouter.ai/api/v1"


def read_key(env_file):
    if env_file:
        for line in Path(env_file).read_text().splitlines():
            match = re.match(r"^\s*(?:export\s+)?OPENROUTER_API_KEY\s*=\s*(.*)$", line)
            if not match:
                continue
            value = match[1].strip()
            if value.startswith(("'", '"')):
                quote = value[0]
                end = value.find(quote, 1)
                if end < 0:
                    raise ValueError("Unclosed quote in API key setting")
                value = value[1:end]
            else:
                value = value.split(" #", 1)[0].strip()
            if value:
                return value
        raise ValueError("The selected env file has no nonempty OpenRouter key")
    value = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not value:
        raise ValueError("Set OPENROUTER_API_KEY or pass --env-file")
    return value


def request(path, key=None, payload=None):
    headers = {"Accept": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Provider error bodies can contain request details. Keep them out of logs.
        raise RuntimeError(f"OpenRouter returned HTTP {exc.code}") from None
    except urllib.error.URLError:
        raise RuntimeError("Cannot reach OpenRouter; check network access") from None


def is_free_tool_model(model):
    pricing = model.get("pricing", {})
    try:
        free = all(float(pricing.get(field, -1)) == 0 for field in ("prompt", "completion"))
    except (ValueError, TypeError):
        return False
    return (
        model.get("id", "").endswith(":free")
        and free
        and {"tools", "tool_choice"}.issubset(model.get("supported_parameters") or [])
    )


def run(args):
    catalog = request("/models?supported_parameters=tools")["data"]
    candidates = {model["id"]: model for model in catalog if is_free_tool_model(model)}
    if args.list:
        print(json.dumps({"free_tool_models": sorted(candidates)}, indent=2))
        return
    if not args.model or args.model not in candidates:
        raise ValueError("Choose a currently free tool-capable model from --list")
    key = read_key(args.env_file)
    request("/key", key=key)
    print("API key accepted; value not displayed.", flush=True)

    tool = {
        "type": "function",
        "function": {
            "name": "get_service_health",
            "description": "Read health for the Gada Electronics checkout service.",
            "parameters": {
                "type": "object",
                "properties": {"service": {"type": "string", "enum": ["checkout"]}},
                "required": ["service"],
                "additionalProperties": False,
            },
        },
    }
    messages = [
        {
            "role": "system",
            "content": "Investigate read-only. Use tool evidence. Never claim a fix was applied.",
        },
        {"role": "user", "content": "Check checkout health. Call get_service_health first."},
    ]
    body = {
        "model": args.model,
        "messages": messages,
        "tools": [tool],
        "tool_choice": {"type": "function", "function": {"name": "get_service_health"}},
        "max_tokens": 1024,
        "provider": {"require_parameters": True},
    }
    first = request("/chat/completions", key=key, payload=body)
    if "error" in first:
        raise RuntimeError("Provider returned an inference error; no response body logged")
    message = first["choices"][0]["message"]
    calls = message.get("tool_calls", [])
    if len(calls) != 1:
        raise RuntimeError("Expected one health tool request")
    call = calls[0]
    function = call.get("function", {})
    if function.get("name") != "get_service_health":
        raise RuntimeError("Unexpected tool name")
    if json.loads(function.get("arguments", "{}")) != {"service": "checkout"}:
        raise RuntimeError("Unexpected service arguments")
    print("Structured tool name and arguments verified.", flush=True)

    # Echo the full assistant message: providers may need reasoning metadata.
    messages.append(message)
    messages.append({
        "role": "tool",
        "tool_call_id": call["id"],
        "content": json.dumps({"service": "checkout", "status": "unhealthy", "http_status": 503}),
    })
    body["tool_choice"] = "none"
    second = request("/chat/completions", key=key, payload=body)
    if "error" in second:
        raise RuntimeError("Provider returned an inference error; no response body logged")
    final = second["choices"][0]["message"]
    answer = final.get("content") or ""
    grounded = "503" in answer and any(word in answer.lower() for word in ("unhealthy", "unavailable", "failing", "down"))
    result = {
        "model": args.model,
        "mode": "live",
        "model_requests": 2,
        "tool_exchange_passed": not final.get("tool_calls") and grounded,
        "answer": answer,
        "usage": [first.get("usage", {}), second.get("usage", {})],
        "scope": "Synthetic read-only health check; not full capstone or class-capacity validation",
    }
    # Print only allowlisted usage fields; never dump provider metadata or request headers.
    result["usage"] = [
        {field: usage[field] for field in ("prompt_tokens", "completion_tokens", "total_tokens", "cost") if field in usage}
        for usage in result["usage"]
    ]
    if key in answer:
        result["answer"] = "[redacted]"
        raise RuntimeError("Unexpected sensitive content in answer; suppressed")
    print(json.dumps(result, indent=2))
    if not result["tool_exchange_passed"]:
        raise RuntimeError("Model did not report the supplied health evidence correctly")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", help="Read only OPENROUTER_API_KEY from this file; never source it")
    parser.add_argument("--model", help="Explicit free model ID; no paid fallback")
    parser.add_argument("--list", action="store_true", help="List free tool-capable models; no key needed")
    try:
        run(parser.parse_args())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, IndexError, OSError):
        # Do not print arbitrary exception messages: external content may contain secrets.
        print("Check failed. Verify connectivity, the key, free-model availability, and tool support.", file=sys.stderr)
        sys.exit(1)
