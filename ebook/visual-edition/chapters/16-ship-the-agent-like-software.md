# Ship the agent like software


05 / Operate the system


## What changes when the prompt changes?

Prompts, tool schemas, models and knowledge indexes can change behavior as much as application code. Release them with visible versions, relevant checks and a recovery plan.



**Version.** Code, prompts, schemas, configuration and index build identity.


**Gate.** Run boundary tests and representative behavior checks.


**Operate.** Observe changes, limit exposure and keep rollback options.


## A release is a set of compatible parts

A prompt tested with one tool schema may fail with another. Preserve the combination that produced the observed result.


### Diagram reading order


1. **Build:** Resolve dependencies and create a reproducible artifact.

2. **Validate:** Check contracts, permissions and selected evaluations.

3. **Release:** Promote a versioned configuration under explicit policy.

4. **Observe / roll back:** Compare real outcomes and restore a known combination if needed.



Avoid exposing deployment credentials to untrusted pull-request code. Give automation the smallest permissions it needs.


## A model upgrade changes tool behavior

The new model omits a required resource identifier in some tool requests.



1. **Detect:** Contract checks reject invalid requests before dispatch.

2. **Compare:** Run the same reviewed task set against both configurations.

3. **Contain:** Keep the old version serving while investigating the regression.

4. **Promote:** Release only after the new combination meets the chosen criteria.



Model aliases and provider behavior can change independently of your code. Record the most precise identity available and keep monitoring.


## Failure and correction

CI only lints Python, so a prompt edit that recommends disabling tests is released without a behavior check.



Make evaluation inputs part of release review. Treat a new dangerous recommendation as a release regression.


## Engineering review


- Pin what can be pinned.

- Protect CI credentials.

- Record the released combination.

- Practice recovery from regressions.


## Further reading


- [GitHub Actions: secure use](https://docs.github.com/en/actions/reference/security/secure-use)

- [GitHub Actions: token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)

- [Anthropic: agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)
