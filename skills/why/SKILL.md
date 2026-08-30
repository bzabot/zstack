---
name: why
description: "Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds."
---

# Why

Investigate the motivation and intent behind code. `how` explains what the code does; `why` explains the forces that shaped it.

## Workflow

### 1. Understand the question

Identify the target and the kind of explanation needed:

- design rationale or a tradeoff
- an edge case or defensive behavior
- a product, business, or operational constraint
- a regression, incident, or threshold
- why existing code still exists

If the target is vague, state your best interpretation and proceed. Let the user redirect if needed.

### 2. Establish the code anchor

Before investigating history, identify:

- relevant file paths and line ranges
- key symbols, constants, and behavior
- recent commits and blame for the target
- linked PRs, tickets, or documents

Read the code to understand what the target is, but do not treat its mechanics as evidence of intent. Use source control history and linked discussions to establish the initial context.

```bash
# Blame target lines for last-touch commits
git blame -L <start>,<end> <file>

# Full file history, with patches, through renames
git log --follow -p -- <file>

# Last N commits touching the file, PR numbers visible
git log --oneline -20 -- <file>

# Extract PR numbers from a commit message
git log -1 --format=%B <commit>
```

### 3. Gather evidence

Start with source control. Then search the available sources that are relevant to the question: issue trackers, design documents, team discussions, incident records, observability, error tracking, or product analytics. Use the matching source playbook in `references/sources/` when one exists.

For defensive behavior, also use `references/sources/incident-postmortem.md` as a cross-cutting search angle.

For a simple question, investigate in one pass. For a complex question, spawn parallel investigators for distinct sources or angles, then synthesize their findings.

Each investigator should:

- Use the built-in explorer role with a unique `task_name`.
- Usually inherit the parent's model. If overriding it, choose an available `model` and matching `reasoning_effort`.
- Instruct the agent not to mutate files or external state. Use a custom agent profile with `sandbox_mode = "read-only"` when hard enforcement is required.

Give each investigator the original question, the code anchor, and the relevant instructions from `references/investigator-prompt.md` and the source playbook. Investigators gather evidence rather than writing the final answer. They return what they searched, direct evidence with precise citations, indirect evidence and its inference chain, contradictions, gaps, and additional leads.

Do not search every source by default. Choose sources that can answer the question, and state when an unavailable or unsearched source leaves a gap.

### 4. Synthesize

For complex or delegated investigations, spawn one subagent to synthesize the findings:

- Use the built-in default role with a unique `task_name`.
- Usually inherit the parent's model. If overriding it, choose an available `model` and matching `reasoning_effort`.
- Instruct the agent not to mutate files or external state.

Give it the investigator findings, code anchor, original question, `references/epistemics.md`, and `references/synthesizer-prompt.md`. It should reconcile overlapping evidence, surface contradictions, distinguish facts from inferences, and avoid filling gaps with a plausible story.

For a simple question investigated in one pass, the investigating agent may produce the final answer directly.

### 5. Present

Present the answer with enough context for the reader to verify it. Lightly edit delegated output for clarity, but preserve its confidence level and citations.

## Evidence rules

- The code explains what happens, not necessarily why it exists.
- Cite every claim about intent with a commit, PR, ticket, document, conversation, or explicit code comment.
- Separate direct evidence from supported conclusions, inferences, and speculation.
- Use hedged language when evidence is indirect.
- Surface contradictions instead of choosing the tidier story.
- Report what was not found and which sources were unavailable.
- Treat a hypothesis in the user's question as a hypothesis to test, not as a conclusion.

## Output format

Adapt the structure to the question, but keep the evidence boundaries visible:

### The Question

Restate the question briefly.

### The Code in Question

Give the relevant paths, line ranges, and symbols.

### What We Found

List claims supported by direct citations. Mark claims supported by multiple indirect sources as supported.

### What We Can Reasonably Infer

Explain the inference chain and use language such as “appears to,” “likely,” or “suggests.”

### Competing Hypotheses

Include this when multiple explanations fit the evidence. Give evidence for and against each one.

### What We Don’t Know

Name unanswered questions, empty searches, and unavailable sources specifically.

### Sources Consulted

List the sources actually searched and what each contributed.

### Confidence Summary

Summarize what is directly established, what is inferred, and what remains unknown.

## Common failure modes

- Confident storytelling from thin evidence
- Treating code mechanics as proof of intent
- Agreeing with the user’s proposed explanation without checking it
- Hiding contradictions or gaps
- Presenting a source as searched when it was unavailable or not searched

## Reference files

- `references/epistemics.md`: confidence tiers and phrasing guidance
- `references/investigator-prompt.md`: investigator prompt template
- `references/source-playbook.md`: source playbook index
- `references/sources/*.md`: source-specific investigation guidance
- `references/synthesizer-prompt.md`: synthesizer prompt and output guidance
