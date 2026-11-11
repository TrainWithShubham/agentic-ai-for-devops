"""A small, read-only tool exchange before the full LangGraph workflow."""

import argparse
import asyncio
import json

from runbookops.config import Settings
from runbookops.models import Model, tool_call
from runbookops.rag import Retriever
from runbookops.security import principal
from runbookops.store import open_store
from runbookops.tools import SCHEMAS, Tools


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["offline", "openrouter", "groq", "bedrock"], default="offline")
    args = parser.parse_args()
    settings = Settings.load(mode=args.mode)
    actor = principal("bagha")
    store = open_store(settings)
    case = store.create_incident(actor)
    tools = Tools(store, Retriever(settings), actor, case["id"])
    model = Model(settings)
    messages = [
        {
            "role": "system",
            "content": "Check checkout health using the supplied tool. After its result, explain the status. Never claim to fix anything.",
        },
        {"role": "user", "content": "Check current checkout health."},
    ]
    if args.mode == "offline":
        response = {
            "role": "assistant",
            "content": None,
            "tool_calls": [tool_call("get_service_health", {"service": "checkout"}, 1)],
        }
    else:
        response, _ = await model.complete(messages, SCHEMAS[:1])
    print("Mode:", args.mode)
    messages.append(response)
    for call in response.get("tool_calls", []):
        if call["function"]["name"] != "get_service_health":
            raise ValueError("Only the health tool is available here")
        arguments = json.loads(call["function"]["arguments"])
        print("Tool requested:", call["function"]["name"], arguments)
        result = tools.call("get_service_health", arguments)
        print("Validated result:", result)
        messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
    if args.mode == "offline":
        print("Offline fixture: checkout is unhealthy and returns HTTP 503. No change was applied.")
    else:
        answer, _ = await model.complete(messages)
        print(answer.get("content"))
    store.close()


if __name__ == "__main__":
    asyncio.run(main())
