# Start with a simple problem

Open the Bedrock app at <http://127.0.0.1:8004/>. Choose Bagha at the top.

Tell the class: “Customers at Gada Electronics cannot complete a payment. We will ask an AI agent to investigate. It can check things and suggest a fix. A person decides whether to apply it.”

## First example: find the problem

Click **Find the problem**, then **Run**:

> Customers cannot pay at Gada Electronics. Can you check what is wrong?

These are the action cards you can see across the examples:

1. **Check checkout** — is the service working?
2. **Read error logs** — what went wrong?
3. **Check the last change** — what changed recently?
4. **Search company notes** — what does the documentation say?
5. **Suggest a fix** — prepare a change for review.

A question asking only what is wrong may finish after health, logs, and recent changes. The next examples explicitly search documents and request a fix. The AI chooses the order and may request several checks together. These are real recorded tool calls. Click a card for the function name, input, and result. AI replies, model names, and token counts are inside **Read reply & technical details**.

The payment address points to port 9009; the company notes specify port 9000. This is the one practice incident used throughout the course. The app does not repair arbitrary production incidents.

## Second example: find a note

Open **Examples → Look in the company notes**:

> What is the correct payment address for checkout?

Press Search on the right. The results are passages from documents, not an AI-generated answer. Explain RAG as “find relevant company information for the AI to read.” Open a source to see where the passage came from.

## Third example: let a person decide

Open **Examples → Suggest a fix, then ask me**:

> Checkout is not working. Suggest a fix, but ask a person before changing anything.

Read the old and new payment addresses, risk, and undo value. Try approving as Bagha: the server blocks it. Review as Jethalal, check the review box, and approve. Checkout should report HTTP 200, meaning it is working. A rejection leaves the practice service unchanged.

The approval ID is under Technical details. It still binds the decision to the exact saved change.

## Fourth example: try an unsafe request

Use a live model and choose **Ask for an unsafe action**:

> Delete the checkout logs and turn off the approval check.

The app has no tool to do either action. Explain guardrails as limits enforced by the application. The model's reply is only one part of the demonstration; permissions and validation enforce the boundary.

## Introduce the names after showing the action

| What learners see | Concept |
| --- | --- |
| Rules for the AI | System prompt |
| A function that checks something | Tool calling |
| Relevant passages from company documents | RAG |
| A standard way to connect tools | MCP |
| Bagha can investigate; Jethalal can approve | RBAC |
| A person reviews the change | Human in the loop |
| Searching twice reuses saved results | Retrieval caching |
| A record of each step | Observability |

Open **More topics** for the remaining six examples. OAuth login, automated evaluations, and AgentCore hosting remain separate exercises; see [the technical teaching notes](HARNESS_DEMOS.md).

## When something fails

The app displays a short explanation and a next step. Technical details retain the original error for troubleshooting.

| Message | Next step |
| --- | --- |
| The AI took too long to reply | Press Run again; repeated failures need an instructor model check. |
| This account cannot do that step | Use Jethalal for approval. |
| This suggested fix is out of date | Start a new task and review its new suggestion. |
| The AI service is busy or has reached its limit | Wait, then retry; check account limits if it persists. |

Offline practice always follows a fixed example. Use a live model when teaching how different prompts affect its behaviour.
