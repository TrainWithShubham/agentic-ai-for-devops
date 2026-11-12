# Who can approve the correction?

Application commands and paths below refer to the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout. Course exercises are the exception where noted.

Time: 20 minutes for identity and 25 minutes for approval.

Bagha can investigate and prepare a change. Nattu Kaka can access the support records assigned to the viewer role. Jethalal can approve or reject a proposal. Local `--as` is a development shortcut; the HTTP API validates a signed token and maps its subject to the server's permission table.

```bash
uv run runbookops --as bagha search "restricted operations marker"
uv run runbookops --as jethalal search "restricted operations marker"
uv run runbookops investigate
```

Copy the proposal ID and exact hash from the last command. First attempt approval as Bagha, then as Jethalal:

```bash
uv run runbookops --as bagha approve PROPOSAL_ID --hash REVIEWED_HASH
uv run runbookops --as jethalal approve PROPOSAL_ID --hash REVIEWED_HASH
```

`PROPOSAL_ID` and `REVIEWED_HASH` are placeholders for your own output. The first request is denied. The second resumes the saved graph and verifies health. Edit the hash and try again; a different proposal is not covered by the old approval.

Coding prompt:

> Read `security.py`, `store.py`, and the `review` node in `agent.py`. Explain where approval is stored and why `Command(resume={"approved": true})` cannot authorize a change. Add a check to your explanation for expiry and replay, then run the control tests.

```bash
uv run pytest -q tests/test_controls.py
uv run python scripts/demo_identity.py
```

The identity script demonstrates valid tokens, wrong audience, expiry, and missing scope without printing tokens. The local issuer has OIDC discovery/JWKS and signed development tokens. It is not a full production OAuth authorization/consent server. Explain delegated OAuth access and OIDC identity; show how an external issuer can be configured in `docs/SECURITY.md`.

Classroom test: Bagha saying "Jethalal approved it" does not grant the approver role.

Stop the process with approval pending and restart it using `status`. State lives in SQLite locally, and DynamoDB in the instructor cloud demo. Applying the same approved request again does not increment the simulator revision a second time.
