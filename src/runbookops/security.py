"""Trusted identities and output redaction. The model never supplies a role."""

import re
from dataclasses import dataclass


class Denied(Exception):
    pass


class InvalidChange(Exception):
    pass


@dataclass(frozen=True)
class Principal:
    user: str
    role: str
    scopes: frozenset[str]


USERS = {
    "bagha": ("viewer", frozenset({"read", "investigate"})),
    "nattu": ("viewer", frozenset({"read", "investigate"})),
    "jethalal": ("approver", frozenset({"read", "investigate", "approve"})),
}


def principal(user: str, scopes=None) -> Principal:
    if user not in USERS:
        raise Denied("Unknown workshop identity")
    role, granted = USERS[user]
    if scopes is not None:
        granted = granted.intersection(scopes)
    return Principal(user, role, frozenset(granted))


def require(actor: Principal, scope: str):
    if scope not in actor.scopes or (scope == "approve" and actor.role != "approver"):
        raise Denied(f"{actor.user} lacks {scope} permission")


def redact(value):
    if isinstance(value, dict):
        return {
            k: "[redacted]"
            if any(word in k.lower() for word in ("secret", "password", "api_key", "authorization", "token"))
            and k not in ("prompt_tokens", "completion_tokens", "total_tokens", "max_tokens")
            else redact(v)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    if isinstance(value, str):
        value = re.sub(r"sk-(?:or-v1-)?[A-Za-z0-9_-]{12,}", "[redacted]", value)
        value = re.sub(r"(?i)Bearer\s+[A-Za-z0-9._-]+", "Bearer [redacted]", value)
        value = re.sub(
            r"(?i)((?:api[_-]?key|password|secret|access_token)\s*[=:]\s*)[^\s,;]+", r"\1[redacted]", value
        )
        return value
    return value
