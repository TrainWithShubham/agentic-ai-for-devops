"""Return current documents allowed for engineer/release-manager. Reject unknown roles.
Each document has current: bool and roles: list[str]. Do not mutate inputs.
"""


def allowed_sources(documents, role):
    raise NotImplementedError("Implement allowed_sources; see solutions/source_filter.py")
