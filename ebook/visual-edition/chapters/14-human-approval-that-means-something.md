# Human approval that means something


04 / Control and approval


## In everyday words

Human approval should allow one exact action. Save what was reviewed and check it again before execution.


## Picture it

Signing a delivery label approves that parcel and address. It should not approve a different parcel later.

A proposal hash detects changes when compared with trusted data; it does not identify the reviewer.



**Proposal.** The action, target and parameters.


**Decision.** An authorized person accepts or rejects it.


**Execution.** Apply only what was approved.


## A proposal has a lifecycle

Record each state. Only an approved, still-valid proposal may reach execution.


### Diagram reading order


1. **Prepared:** Save target, action, evidence and expiry.

2. **Pending review:** Show the exact change.

3. **Decision recorded:** Bind approval or rejection to this proposal.

4. **Applied + verified:** Record the action and observed result.



Rejected means stop. Changed or expired means review again. Use one-time approval and recheck the target before applying.


## The patch changed after approval

The original patch adds a test dependency. The new one disables tests.



1. **Save:** Store the exact patch and trusted digest.

2. **Review:** Show the proposed change and impact.

3. **Compare:** A changed digest invalidates approval.

4. **Re-review:** Require a decision on the new patch.



Use expiry and one-time approval. Recheck target state before applying.


## Failure and correction

Reusing an approval or changing the patch after review.



Bind review to the saved action and prevent replay.


## Engineering review


- Exact parameters.

- Trusted reviewer.

- No approval replay.

- Verified result.


## Further reading


- [OWASP: authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

- [LangGraph: interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

- [OWASP: transaction authorization](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html)
