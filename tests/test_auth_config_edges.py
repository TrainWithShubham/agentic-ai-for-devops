import dataclasses
from pathlib import Path
from types import SimpleNamespace

import jwt
import pytest

from runbookops.auth import Auth
from runbookops.config import Settings
from runbookops.security import Denied, principal


@pytest.mark.parametrize("values", [{"mode": "unknown"}, {"max_calls": 0}, {"max_tokens": 5000}])
def test_invalid_configuration_is_rejected(settings, values):
    with pytest.raises(ValueError):
        dataclasses.replace(settings, **values)


def test_env_file_only_imports_model_settings(settings, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    extra = tmp_path / "external.env"
    extra.write_text(
        "OPENROUTER_MODEL=test:free\nOPENROUTER_API_KEY=synthetic-key\nRUNBOOKOPS_FREE_ONLY=false\nAWS_SECRET_ACCESS_KEY=never-import\nBEDROCK_MODEL_ID=test-bedrock\n"
    )
    configured = Settings.load(extra, root=settings.root, data=tmp_path / "isolated", mode="openrouter")
    assert configured.model == "test:free" and configured.api_key == "synthetic-key"
    assert configured.free_only
    bedrock = Settings.load(extra, root=settings.root, data=tmp_path / "bedrock", mode="bedrock")
    assert bedrock.model == "test-bedrock"
    monkeypatch.setenv("OPENROUTER_MODEL", "environment-wins:free")
    assert (
        Settings.load(extra, root=settings.root, data=tmp_path / "overrides", mode="openrouter").model
        == "environment-wins:free"
    )


@pytest.mark.parametrize("kwargs", [{}, {"oidc_jwks": "http://unsafe.invalid/keys"}])
def test_external_issuer_rejects_missing_or_insecure_trust(settings, kwargs):
    with pytest.raises(ValueError):
        Auth(dataclasses.replace(settings, oidc_issuer="https://issuer.example", **kwargs))


def test_external_jwks_verification_and_key_race(settings, monkeypatch):
    local = Auth(settings)
    exists = Path.exists
    monkeypatch.setattr(Path, "exists", lambda p: False if p == local.key_path else exists(p))
    raced = Auth(settings)
    assert raced.public == local.public
    monkeypatch.setattr(Path, "exists", exists)
    external = Auth(
        dataclasses.replace(settings, oidc_issuer=local.issuer, oidc_jwks="https://issuer.example/keys")
    )
    key = SimpleNamespace(key=local.public)
    monkeypatch.setattr(external.jwk_client, "get_signing_key_from_jwt", lambda token: key)
    assert external.verify(local.issue("bagha")).user == "bagha"

    def invalid(token):
        raise jwt.PyJWKClientError("upstream unavailable")

    monkeypatch.setattr(external.jwk_client, "get_signing_key_from_jwt", invalid)
    with pytest.raises(Denied):
        external.verify("bad-token")
    with pytest.raises(Denied):
        principal("unknown")
