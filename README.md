# Zstack

Zstack is a development workflow plugin for Claude Code and Codex. It gives your coding agent a composable set of skills — one orchestrating workflow (**Zabot Mode**), a library of engineering principles, and a handful of sharp-edged tools — so it specs before it builds, delegates instead of hoarding context, and proves the result against the real app instead of declaring victory early.

## Table of Contents

- [How it works](#how-it-works)
- [Installation](#installation)
  - [Claude Code](#claude-code)
  - [Codex](#codex)
- [The Basic Workflow](#the-basic-workflow)
- [What's Inside](#whats-inside)
- [Philosophy](#philosophy)
- [Verify](#verify)
- [Contributing](#contributing)

## How it works

When you ask your agent to build something, Zstack doesn't let it jump straight into code. Zabot Mode kicks in and shapes the work first: a grilling session to pin down the spec, foundational thinking to get the data structures right, then implementation sequenced into small verifiable units — each one proven against the real artifact before moving on.

Along the way, the principle skills fire automatically: the agent fixes root causes instead of patching symptoms, subtracts before it adds, guards its own context window by delegating bulk work to subagents, and refuses to call anything "done" until it has run the feature and inspected the actual result.

Because the skills trigger on their own, you don't need to do anything special. Your coding agent just works the Zstack way.

## Installation

### Claude Code

Test a local checkout:

```sh
claude --plugin-dir .
```

Validate it:

```sh
claude plugin validate .
```

From a published marketplace:

```text
/plugin marketplace add bzabot/zstack
/plugin install zstack@zstack
```

### Codex

From a local checkout:

```sh
codex plugin marketplace add .
codex plugin add zstack@zstack
```

From a published marketplace:

```sh
codex plugin marketplace add bzabot/zstack
codex plugin add zstack@zstack
```

## The Basic Workflow

1. **grilling** — Start here. The agent interviews you about the plan or idea, resolves its open decisions, and writes a final Markdown spec after your confirmation.
2. **zabot-mode** — Point it at the spec. It shapes the data first, delegates implementation, and proves the result against the real app.
3. **principle-foundational-thinking** — Gets core types and data structures right before any logic, so downstream code becomes obvious.
4. **principle-sequence-verifiable-units** — Breaks the work into small units that each end in a verifiable state, ordered so the sequence proves itself to a reviewer.
5. **principle-prove-it-works** — Verifies against the real artifact (run the feature, read the actual value, inspect the diff) before anything is declared done.

The remaining principles fire as the situation demands — debugging, concurrency, migrations, context pressure.

## What's Inside

### Workflow

- **zabot-mode** — Orchestrating workflow: spec first, delegate implementation, prove it works against the real app.
- **grilling** — Spec interview: resolve every decision in a plan before a line of code is written.
- **create-verification-skill** — Generates a project-local skill that drives your app the way a user does, in any language, framework, or platform.

### Engineering Principles

- **principle-foundational-thinking** — Choose core types and data structures first; get them right and the rest follows.
- **principle-laziness-protocol** — Subtract first, then build the smallest change that solves the problem, measured by the load it puts on the next reader.
- **principle-build-the-lever** — Build the tool that does it or proves it (codemod, script, generator) instead of working by hand.
- **principle-model-the-domain** — Encode the domain in a structure instead of scattered conditionals.
- **principle-fix-root-causes** — Reproduce first, trace each symptom to its root cause, fix it there — no nil-check guards that silence crashes.
- **principle-prove-it-works** — Verify against the real artifact, not a proxy, a self-report, or "it compiles."
- **principle-sequence-verifiable-units** — Small units, each ending in a verifiable state, checked before the next.
- **principle-guard-the-context-window** — Route bulk to subagents; keep summaries in the main thread, not raw payloads.
- **principle-never-block-on-the-human** — Proceed on reversible work and present the result; reserve confirmation for irreversible actions.
- **principle-migrate-callers-then-delete-legacy-apis** — Migrate callers and delete the old API in the same wave; no compatibility layers.
- **principle-separate-before-serializing-shared-state** — Eliminate sharing between concurrent actors first; serialize only when one shared writer is a real invariant.

### Tools

- **ponytail** — Forces the smallest coding solution that fully works. YAGNI as a contact sport.
- **explain-diff** — Explains a change, diff, branch, or PR visually: the smallest useful diagram, or a self-contained interactive HTML walkthrough with a quiz.
- **comment-sicko** — A deranged comment-hater that savors deletion and condemns workaround code.
- **unslop** — Cuts AI tells from any writing.

## Philosophy

- **Spec before code** — Decisions get resolved in conversation, not discovered in review.
- **Evidence over claims** — Nothing is done until it's proven against the real artifact.
- **Subtraction first** — The best change is the smallest one that fully works.
- **The tool over the hand** — If it's worth doing, it's worth building the lever that does it.

## Verify

Run the package tests:

```sh
python3 -m unittest discover -s tests -v
```

## Contributing

1. Fork the repository.
2. Create a branch for your work.
3. Add or modify skills under `skills/`, each self-contained in its own folder with a `SKILL.md`.
4. Run the tests above before submitting a PR.
