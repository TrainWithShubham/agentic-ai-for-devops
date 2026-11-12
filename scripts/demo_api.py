"""Exercise the running local API without printing access tokens."""

import argparse

import httpx

from runbookops.auth import Auth
from runbookops.config import Settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    auth = Auth(Settings.load())
    with httpx.Client(base_url=args.base_url, timeout=180) as client:
        bagha = {"Authorization": "Bearer " + auth.issue("bagha")}
        jethalal = {"Authorization": "Bearer " + auth.issue("jethalal")}
        assert client.get("/me").status_code == 401
        state = client.post(
            "/investigations",
            headers=bagha,
            json={"question": "Investigate checkout and prepare a correction for approval."},
        )
        state.raise_for_status()
        proposal = state.json().get("proposal")
        if not proposal:
            raise RuntimeError("Investigation did not reach approval: " + str(state.json().get("error")))
        request = {"expected_hash": proposal["hash"], "approve": True}
        assert (
            client.post(f"/proposals/{proposal['id']}/decision", headers=bagha, json=request).status_code
            == 403
        )
        approved = client.post(f"/proposals/{proposal['id']}/decision", headers=jethalal, json=request)
        approved.raise_for_status()
        assert approved.json()["health"]["http_status"] == 200
    print(
        "HTTP API passed: anonymous denied, Bagha approval denied, Jethalal approval recovered checkout. Tokens not displayed."
    )


if __name__ == "__main__":
    main()
