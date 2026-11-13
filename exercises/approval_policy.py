"""Return True only for release-manager, expires_at > now, and already_approved is False.
This is a policy predicate, not token validation or an approval executor.
"""


def may_approve(role, expires_at, now, already_approved):
    raise NotImplementedError("Implement may_approve; see solutions/approval_policy.py")
