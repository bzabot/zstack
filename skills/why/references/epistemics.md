# Epistemics

Code shows what happens. Motivation usually lives in history, discussions, documents, and operational evidence. Do not turn the current code into a story about why it exists.

## Confidence tiers

Put every claim in the tier that its evidence supports:

- **Direct:** an explicit statement in a commit, PR, ticket, document, conversation, test, or code comment. Cite it and state it plainly.
- **Supported:** several indirect sources converge. Cite the sources and explain what each contributes.
- **Inferred:** a reasonable interpretation with no explicit statement. Use “appears to,” “likely,” or “suggests,” and show the inference chain.
- **Speculative:** one plausible hypothesis among others. Mark it as a possibility and state that direct evidence is missing.
- **Unknown:** you searched and could not establish the answer. Say what you searched and what was unavailable.

## Rules

- Cite every claim about intent with a precise source: commit hash, PR, ticket, document, conversation, test, or file:line.
- Do not cite code mechanics as proof of intent. An explicit comment may be evidence; a function name or branch is not.
- Use confident causal language such as “because” only for direct evidence. Hedge indirect claims.
- Surface contradictory evidence instead of choosing the tidier explanation.
- Treat a hypothesis in the user's question as a candidate to test.
- Do not treat an absence of evidence as evidence that something did not happen.
- Prefer an honest gap over a plausible, unsupported explanation.

## Final check

Before returning:

1. Does every direct or supported claim have a citation?
2. Is each claim phrased for its confidence tier?
3. Is any code being used as evidence of its own intent?
4. Are contradictions and meaningful gaps visible?
