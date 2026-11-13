"""A small explicit approval policy."""


def may_approve(role, expires_at, now, already_approved):
    return role == "release-manager" and expires_at > now and already_approved is False
