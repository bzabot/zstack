# Synthesizer Prompt Template

Build the synthesizer's prompt from this template and fill in the placeholders.

---

Answer the following "why" question by weighing the investigator findings. Produce a concise, evidence-cited answer that separates facts from inferences and is honest about gaps.

## The Question

> {QUESTION}

## The Code Anchor

**Target files:** {FILES_WITH_LINE_RANGES}

**Key symbols:** {SYMBOLS}

## Investigator Findings

{ALL_INVESTIGATOR_FINDINGS}

## Sources Not Searched

{SKIPPED_SOURCES_WITH_REASONS}

## Rules

Read `references/epistemics.md` and apply it:

- Cite every direct or supported claim.
- Label inferences and speculation, and hedge them.
- Do not use code mechanics as proof of intent.
- Surface contradictions rather than resolving them silently.
- State specific gaps and unavailable sources.
- Test the user's hypothesis instead of accepting it.

Read all findings before writing. Reconcile duplicate evidence, verify citations with available read-only tools when necessary, and do not modify files or external state.

## Output

### The Question

Restate the question briefly.

### The Code in Question

List the relevant paths, line ranges, and symbols.

### What We Found

List direct claims with citations. Mark conclusions supported by several indirect sources.

### What We Can Reasonably Infer

List useful inferences with their evidence chain and calibrated language.

### Competing Hypotheses

Include only when multiple explanations fit. Give evidence for and against each one.

### What We Don’t Know

List unanswered questions, empty searches, and unavailable sources specifically.

### Sources Consulted

List what was actually searched and what each source contributed.

### Confidence Summary

Summarize what is directly established, what is inferred, and what remains unknown.

## Final check

Before returning, confirm that:

1. Direct and supported claims have citations.
2. Confidence language matches the evidence.
3. Contradictions and gaps are visible.
4. No code mechanic is presented as intent.
