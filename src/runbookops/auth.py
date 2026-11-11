"""JWT validation and a local development issuer for the identity exercise."""

import json
import os
import time
import uuid

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .security import USERS, Denied, principal


class Auth:
    def __init__(self, settings):
        self.settings = settings
        self.issuer = (
            os.getenv("RUNBOOKOPS_OIDC_ISSUER") or settings.oidc_issuer or "http://127.0.0.1:8000/oidc"
        )
        self.audience = os.getenv("RUNBOOKOPS_OIDC_AUDIENCE") or settings.oidc_audience
        self.external = bool(os.getenv("RUNBOOKOPS_OIDC_ISSUER") or settings.oidc_issuer)
        self.key_path = settings.data / "dev-issuer.pem"
        if self.external:
            self.public = (os.getenv("RUNBOOKOPS_OIDC_PUBLIC_KEY") or settings.oidc_public_key).replace(
                "\\n", "\n"
            )
            self.jwks = os.getenv("RUNBOOKOPS_OIDC_JWKS") or settings.oidc_jwks
            if not self.public and not self.jwks:
                raise ValueError(
                    "External issuer requires RUNBOOKOPS_OIDC_JWKS or RUNBOOKOPS_OIDC_PUBLIC_KEY"
                )
            if self.jwks and not self.jwks.startswith("https://"):
                raise ValueError("External JWKS must use HTTPS")
            self.jwk_client = jwt.PyJWKClient(self.jwks) if self.jwks else None
        else:
            if not self.key_path.exists():
                key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                encoded = key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
                try:
                    fd = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(encoded)
                except FileExistsError:
                    pass
            key = serialization.load_pem_private_key(self.key_path.read_bytes(), password=None)
            self.public = (
                key.public_key()
                .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
                .decode()
            )
            self.jwk_client = None

    def issue(self, user, scopes=None, audience=None, expires=600):
        if self.external:
            raise Denied("Use the external issuer login flow; local issuance is disabled")
        actor = principal(user)
        scopes = actor.scopes if scopes is None else frozenset(scopes)
        if not scopes.issubset(USERS[user][1]):
            raise Denied("Cannot issue scopes outside the user permission set")
        now = int(time.time())
        return jwt.encode(
            {
                "iss": self.issuer,
                "aud": audience or self.audience,
                "sub": user,
                "iat": now,
                "exp": now + expires,
                "scope": " ".join(sorted(scopes)),
                "jti": uuid.uuid4().hex,
            },
            self.key_path.read_bytes(),
            algorithm="RS256",
            headers={"kid": "workshop-local"},
        )

    def verify(self, token):
        try:
            key = self.jwk_client.get_signing_key_from_jwt(token).key if self.jwk_client else self.public
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            )
            return principal(claims["sub"], claims.get("scope", "").split())
        except (jwt.PyJWTError, ValueError, KeyError):
            raise Denied("Invalid, expired, or incorrectly scoped access token") from None

    def jwks_document(self):
        key = serialization.load_pem_public_key(self.public.encode())
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key))
        return {"keys": [{**jwk, "kid": "workshop-local", "use": "sig", "alg": "RS256"}]}
