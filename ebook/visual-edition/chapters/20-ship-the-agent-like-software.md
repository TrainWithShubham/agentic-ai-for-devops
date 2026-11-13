# Ship the agent like software


05 / Operate the system


## In everyday words

Ship prompts, tools and model settings with the same care as code. Keep versions, checks and a way back to a known working combination.


## Picture it

An assembly line needs parts that fit. Changing one part can break the whole product.

A passing check reduces risk; it does not prove every future response will be correct.



**Version.** Know which parts were released.


**Gate.** Check before promotion.


**Recover.** Restore a known combination when needed.


## A release is a set of compatible parts

Review the combination of code, prompt, tool schema, model and knowledge index.


### Diagram reading order


1. **Build:** Create a reproducible artifact.

2. **Validate:** Check rules and representative cases.

3. **Release:** Promote a versioned combination.

4. **Observe / roll back:** Watch outcomes and recover from regressions.



Keep deployment credentials away from untrusted pull-request code. Scope automation permissions. Record model identity; aliases and provider behavior can change.


## A new model omits a field

Tool requests arrive without a required resource ID.



1. **Detect:** Reject the invalid request.

2. **Compare:** Run reviewed cases against both versions.

3. **Contain:** Keep the known version serving.

4. **Promote:** Release after the new combination meets the checks.



Record precise model identity when available. Aliases and provider behavior can change.


## Failure and correction

Testing only Python syntax after changing an important prompt.



Review behavior changes before release.


## Engineering review


- Version the parts.

- Protect CI access.

- Test behavior.

- Keep recovery options.


## Further reading


- [GitHub Actions: secure use](https://docs.github.com/en/actions/reference/security/secure-use)

- [GitHub Actions: token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)

- [Anthropic: agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)
