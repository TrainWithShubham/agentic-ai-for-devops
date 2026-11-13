"""Actual Python role/hash/expiry checks over an in-memory proposal; no CI writes or OAuth server."""

import hashlib
import json
import time
from dataclasses import dataclass

from .common import run_cli, show

ALLOWED_PATCH = {"run_id": 1042, "before": "uv sync --frozen --no-dev", "after": "uv sync --frozen"}


@dataclass(frozen=True)
class Principal:
    user: str
    role: str


def fingerprint(change):
    return hashlib.sha256(json.dumps(change, sort_keys=True).encode()).hexdigest()


class Review:
    def __init__(self):
        self.proposal = None
        self.approved = False

    def prepare(self, actor, change):
        if actor.role not in ("engineer", "release-manager"):
            raise PermissionError("Caller cannot prepare a proposal")
        if change != ALLOWED_PATCH:
            raise ValueError("Only the documented synthetic CI change is permitted")
        self.proposal = {"change": dict(change), "hash": fingerprint(change), "expires_at": time.time() + 300}
        self.approved = False
        return dict(self.proposal)

    def approve(self, actor, expected_hash):
        if actor.role != "release-manager":
            raise PermissionError("Release-manager approval required")
        if not self.proposal or self.approved:
            raise ValueError("No pending proposal")
        if time.time() >= self.proposal["expires_at"]:
            raise ValueError("Proposal expired; prepare a fresh review")
        if expected_hash != self.proposal["hash"] or fingerprint(self.proposal["change"]) != expected_hash:
            raise ValueError("Proposal changed; request fresh approval")
        self.approved = True
        return {
            "status": "approved in memory",
            "ci_modified": False,
            "next_step": "A real executor would separately verify authorization and idempotency",
        }


def main():
    print("Development principals supplied by Python. This example does not validate OAuth/JWT tokens.")
    engineer, manager = Principal("dev-user", "engineer"), Principal("release-owner", "release-manager")
    review = Review()
    proposal = review.prepare(engineer, ALLOWED_PATCH)
    show({"proposal": proposal})
    for actor, digest in ((engineer, proposal["hash"]), (manager, "0" * 64)):
        try:
            review.approve(actor, digest)
        except (PermissionError, ValueError) as error:
            show({"denied": str(error)})
    show(review.approve(manager, proposal["hash"]))
    try:
        review.approve(manager, proposal["hash"])
    except ValueError as error:
        show({"replay_denied": str(error)})


if __name__ == "__main__":
    run_cli(main, "See module-4/README.md or checkpoints/README.md for the next step.")
