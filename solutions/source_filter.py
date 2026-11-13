"""Filter before source text reaches the model."""


def allowed_sources(documents, role):
    if role not in ("engineer", "release-manager"):
        raise ValueError("Unknown role")
    return [doc for doc in documents if doc.get("current") is True and role in doc.get("roles", [])]
