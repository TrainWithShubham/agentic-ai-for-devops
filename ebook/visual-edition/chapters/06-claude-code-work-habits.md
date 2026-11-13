# Claude Code work habits


01 / Foundations


## In everyday words

Claude Code can read files, propose edits and run tools. Give it a small task, then inspect what changed and what checks ran.


## Picture it

Like working with a carpenter: agree on the change, inspect the work and measure the result.

A coding agent can make mistakes. Its completion message is not proof that the checks passed.



**Explore.** Find the relevant code first.


**Plan.** Understand a larger change before editing.


**Verify.** Read the diff and actual check output.


## Give instructions, then enforce boundaries

Keep project instructions short. Use permissions to control access and real checks to judge the result.


### Diagram reading order


1. **CLAUDE.md:** Project facts, conventions and check commands.

2. **Plan + scope:** One change and its affected files.

3. **Permissions:** Only the tools and access needed.

4. **Review + check:** Read the patch and run relevant checks.



Skills hold reusable instructions. Hooks run configured actions at lifecycle events. Review both before using them.


## One change you can explain

A Python build skipped test dependencies, then tried to run pytest.



1. **Explore:** Find the install step. Explain the mismatch before editing.

2. **Plan:** Install the declared test group. Keep the tests.

3. **Change:** Make only the agreed patch. Show the diff.

4. **Verify:** Report actual check results and anything not run.



Watch in Hindi, then explain one change yourself. Features may change after this edition.


## Failure and correction

Allowing everything and accepting a huge patch because the agent says "done".



Keep scope small. Review permissions, the diff and real results.


## Engineering review


- Short project instructions.

- Small changes.

- Reviewed commands.

- Actual check results.


## Further reading


- [Claude Code: best practices](https://code.claude.com/docs/en/best-practices)

- [Claude Code: CLAUDE.md and memory](https://code.claude.com/docs/en/memory)

- [Claude Code: permission boundaries](https://code.claude.com/docs/en/permissions)

- [Claude Code: skills](https://code.claude.com/docs/en/skills)

- [Claude Code: hooks](https://code.claude.com/docs/en/hooks-guide)

- [TWS: Claude Code In One Shot / Hindi](https://www.youtube.com/watch?v=14K2noGTJ1M)
