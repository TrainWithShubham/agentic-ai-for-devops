# Claude Code work habits


01 / Foundations


## How do you learn while it writes code?

Claude Code can inspect a codebase, edit files and run tools under its configured permissions. You remain responsible for understanding the change. Start with a small task you can inspect and verify.



**Explore.** Ask where the behavior lives before requesting a patch.


**Plan.** Use Plan mode to understand a nontrivial change first.


**Verify.** Read the diff and actual check output before accepting the work.


## Give instructions, then enforce boundaries

Keep CLAUDE.md short: project facts, conventions and real check commands. It is context for the model. Permissions, sandboxing and appropriate hooks serve different enforcement purposes.


### Diagram reading order


1. **CLAUDE.md:** Record the relevant project structure and verification commands.

2. **Plan + scope:** Choose one change and identify the files it should affect.

3. **Permissions:** Grant only the tools, paths and environment access needed.

4. **Review + check:** Inspect the patch, run the relevant checks and explain the result.



Skills package reusable instructions. Hooks run at lifecycle events and can automate checks. Review their code and sources; both can add behavior you did not expect.


## One small, reviewable change

A fictional Python CI job installs only runtime dependencies, then tries to run pytest. Work in an isolated branch or checkout without production credentials.



1. **Explore:** Find the install step and declared test dependency. Explain the mismatch; do not edit yet.

2. **Plan:** Propose the smallest change that installs the declared test group. Keep the test step intact.

3. **Implement:** Make only the agreed change. Summarize the diff and any assumption.

4. **Verify:** Run the available relevant checks. Report exact results and anything you could not run.



Watch the Hindi lesson, then explain one change without reading the generated answer. Menu names and permission behavior may change after this edition.


## Failure and correction

A learner enables broad permission bypass, asks for a whole platform and accepts a large patch because Claude reports that tests passed.



Use a small scope and normal permission checks. Read the actual diff and test result; reject test removal or fabricated verification. Keep secrets outside the accessible learning environment.


## Engineering review


- Keep project instructions concise.

- Explore and plan before broad edits.

- Review commands, permissions and the diff.

- Ask for exact checks and unresolved limits.


## Further reading


- [Claude Code: best practices](https://code.claude.com/docs/en/best-practices)

- [Claude Code: CLAUDE.md and memory](https://code.claude.com/docs/en/memory)

- [Claude Code: permission boundaries](https://code.claude.com/docs/en/permissions)

- [Claude Code: skills](https://code.claude.com/docs/en/skills)

- [Claude Code: hooks](https://code.claude.com/docs/en/hooks-guide)

- [TWS: Claude Code In One Shot / Hindi](https://www.youtube.com/watch?v=14K2noGTJ1M)
