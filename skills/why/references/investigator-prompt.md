# Investigator Prompt Template

Build each investigator's prompt from this template. Add the relevant guidance from `sources/` when it exists. Investigators may work in parallel, but each should own a distinct source or angle.

---

You are investigating the historical context and motivation behind a piece of code. Gather evidence for a later synthesis; do not write the final answer.

## The Question

> {QUESTION}

## The Code Anchor

**Target files:** {FILES_WITH_LINE_RANGES}

**Key symbols:** {SYMBOLS}

**Relevant history:** {COMMIT_LIST}

**Linked PRs or tickets:** {PR_NUMBERS_AND_TICKET_IDS}

## Your Assigned Source or Angle

{SOURCE_NAME}

{SOURCE_GUIDANCE}

## Investigation Instructions

1. Search broadly enough to find relevant context, then read promising records fully.
2. Stay within your assigned source or angle. Record cross-source leads for the synthesizer instead of duplicating another investigator's work.
3. Capture exact quotes or accurate paraphrases with precise citations: commit hash, PR, ticket, document, conversation, or file:line.
4. Record what you searched, including empty searches and unavailable sources.
5. Surface contradictions and preserve uncertainty. Do not turn a plausible explanation into a fact.

The code anchor explains what the target does. Treat intent as established only by explicit historical evidence; otherwise label it as supported, inferred, speculative, or unknown.

## Return findings in this structure

### Source

What source or angle you investigated.

### What I Searched

Queries, records, files, and tools used.

### Direct Evidence Found

For each item: what it says, where it came from, author/date if available, and why it matters.

### Indirect Evidence

For each item: what it suggests, the inference chain, and any alternative reading.

### Contradictions

Evidence that points to different explanations, with citations.

### Gaps

Questions the source did not answer, empty searches, and access limitations.

### Additional Leads

References to other sources worth checking.
