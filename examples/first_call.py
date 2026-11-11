"""One prompt and one response. No operational tool access."""

import argparse
import asyncio
from pathlib import Path

from runbookops.config import Settings
from runbookops.models import SYSTEM, Model


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["offline", "openrouter", "groq", "bedrock"], default="offline")
    parser.add_argument("--prompt-file", type=Path)
    args = parser.parse_args()
    settings = Settings.load(mode=args.mode)
    prompt = args.prompt_file.read_text() if args.prompt_file else SYSTEM
    response, usage = await Model(settings).complete(
        [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": "Gada Electronics checkout returns HTTP 503. What does this tell us, and what evidence do we need next?",
            },
        ]
    )
    print("Mode:", args.mode)
    print(response.get("content"))
    print("Provider metadata:", usage)


if __name__ == "__main__":
    asyncio.run(main())
