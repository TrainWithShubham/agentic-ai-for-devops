"""Show JWT checks without printing the tokens."""

from runbookops.auth import Auth
from runbookops.config import Settings
from runbookops.security import Denied, require


def main():
    auth = Auth(Settings.load())
    print("Valid Bagha token:", auth.verify(auth.issue("bagha")).role)
    for name, token in [
        ("wrong audience", auth.issue("bagha", audience="other-service")),
        ("expired", auth.issue("bagha", expires=-1)),
    ]:
        try:
            auth.verify(token)
            raise AssertionError("Invalid token accepted")
        except Denied:
            print(name + ": denied")
    try:
        require(auth.verify(auth.issue("bagha", scopes=["read"])), "investigate")
        raise AssertionError("Missing scope accepted")
    except Denied:
        print("Missing investigate scope: denied")
    print("Tokens were not displayed. Local issuer is for development only.")


if __name__ == "__main__":
    main()
