from fastapi.testclient import TestClient

from runbookops.api import create_app


def test_authenticated_incident_and_approval(settings):
    app = create_app(settings)
    auth = app.state.auth
    bagha = {"Authorization": "Bearer " + auth.issue("bagha")}
    jethalal = {"Authorization": "Bearer " + auth.issue("jethalal")}
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/me").status_code == 401
        assert client.get("/me", headers={"Authorization": "Bearer invalid"}).status_code == 401
        assert client.get("/me", headers=bagha).json()["role"] == "viewer"
        assert (
            client.post(
                "/investigations",
                headers=bagha,
                json={"question": "Investigate checkout 503.", "role": "approver"},
            ).status_code
            == 422
        )
        state = client.post(
            "/investigations",
            headers=bagha,
            json={"question": "Investigate checkout 503 and prepare a proposal."},
        ).json()
        p = state["proposal"]
        decision = {"expected_hash": p["hash"], "approve": True}
        assert client.post(f"/proposals/{p['id']}/decision", headers=bagha, json=decision).status_code == 403
        result = client.post(f"/proposals/{p['id']}/decision", headers=jethalal, json=decision)
        assert result.status_code == 200
        assert result.json()["health"]["http_status"] == 200
        assert (
            client.post(f"/proposals/{p['id']}/decision", headers=jethalal, json=decision).status_code == 409
        )
        assert client.get("/oidc/jwks.json").json()["keys"][0]["kty"] == "RSA"
        assert (
            client.post(
                "/invocations",
                headers=bagha,
                json={"operation": "status", "incident_id": state["incident_id"]},
            ).status_code
            == 200
        )


def test_scope_and_cross_user_isolation(settings):
    app = create_app(settings)
    auth = app.state.auth
    with TestClient(app) as client:
        no_scope = {"Authorization": "Bearer " + auth.issue("bagha", scopes=[])}
        assert (
            client.post("/investigations", headers=no_scope, json={"question": "Investigate."}).status_code
            == 403
        )
        bagha = {"Authorization": "Bearer " + auth.issue("bagha")}
        nattu = {"Authorization": "Bearer " + auth.issue("nattu")}
        state = client.post("/investigations", headers=bagha, json={"question": "Investigate."}).json()
        assert client.get("/incidents/" + state["incident_id"], headers=nattu).status_code == 403
        bad_aud = {"Authorization": "Bearer " + auth.issue("bagha", audience="wrong")}
        assert client.get("/me", headers=bad_aud).status_code == 401
