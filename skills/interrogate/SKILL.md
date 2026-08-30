---
name: interrogate
description: 'Use for "interrogate", "adversarial review", "multi-model review", "challenge this", "stress test this code", "find blind spots", or "tear this apart". Multiple LLM reviewers challenge changes from independent angles.'
---

# Interrogate

Use multiple independent reviewers to challenge a change. Give each reviewer the same intent, code, and rubric. Model diversity can expose different blind spots. Agreement is a stronger signal, while lone findings still deserve review.

The deliverable is a synthesized verdict. Do not auto-apply changes.

## 1. Determine scope and intent

Identify what to review from context:

- If the user points at specific files or a diff, use that
- If on a feature branch, inspect the full diff against the appropriate base branch
- If the user's message references recent work, gather the relevant files

Package the diff (or file contents) plus any surrounding context files the reviewers need to understand the code.

State the intent explicitly. Derive it from:

- The user's message
- Commit messages
- PR description if one exists
- The code itself

Write one clear paragraph. Reviewers challenge whether the work achieves the intent well, not whether the intent itself is correct. If the intent is ambiguous, state the best-supported assumption you are reviewing against.

## 2. Spawn reviewers

Choose the number of reviewers for the scope. Launch them in parallel when there is more than one. Use different models when available and useful. If only one model is available, use it for multiple independent reviews.

For each reviewer, use the built-in explorer role and a unique `task_name`. Usually inherit the parent's model. When an override is useful, set an available `model` and `reasoning_effort` that can reliably perform the review. Tell reviewers not to mutate files or external state. This is an instruction, not a permission boundary; use a custom agent profile with `sandbox_mode = "read-only"` when hard enforcement is required.

Read `references/reviewer-prompt.md` and fill in the template with:

1. The stated intent
2. The diff or file contents
3. The review rubric from `references/rubric.md`
4. The code-quality lens from `references/code-quality-review.md`

Send the same filled template to all reviewers. Vary the model, not the review contract.

Each reviewer produces structured findings as described in the prompt template.

## 3. Synthesize findings

As results come back, build a unified picture:

1. **Parse all findings** from the reviewers
2. **Identify consensus**. Findings raised by 2+ models independently are highest signal.
3. **Identify lone-model findings**. Still worth reading, but weight accordingly.
4. **Deduplicate**. Different models may describe the same issue differently. Merge these and note which models raised it.
5. **Note disagreements**. If one model flags something and another explicitly says the opposite, that's useful context for the verdict.

## 4. Apply lead judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator.

Read `references/lead-judgment.md` for the full framework. Reviewers only see a slice of the codebase. You have the full context (the goal, the constraints, the timeline, which tradeoffs were already considered). Use that context aggressively.

Categorize every finding using these buckets:

- **Act on**. Real issues affecting correctness, security, or maintainability given the actual goals. These would block a real PR.
- **Consider**. Legitimate points, but you're not sure they outweigh the cost of addressing them right now. Worth the user's attention.
- **Noted**. Technically valid but not actionable. Context-dependent, premature optimization, or low-impact given the current stage.
- **Dismissed**. Wrong, nitpicky, or missing context. Brief explanation why.

For each finding, include:

- Which model(s) raised it
- The category (act on / consider / noted / dismissed)
- A one-line rationale for the categorization

## Output Format

Present the verdict in this structure:

### Intent

> [The stated intent paragraph from section 1]

### Reviewers

- Reviewer [label]: [model name], [N findings] (one bullet per reviewer)

### Act On

[Findings that should be addressed. For each: description, which models raised it, why it matters.]

### Consider

[Findings worth thinking about. For each: description, which models raised it, tradeoff involved.]

### Noted

[Valid but low-priority. Brief list.]

### Dismissed

[Rejected findings with brief rationale. This shows the user what was filtered out and why, so they can override your judgment if they disagree.]

### Agreement Map

[Where did models agree, where did they diverge, and what does the pattern of agreement/disagreement tell us?]
