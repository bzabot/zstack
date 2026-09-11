---
name: explain-diff
description: Explain a code change, diff, branch, pull request, or the current topic visually. Answers in chat with the smallest useful diagram — pseudocode, call tree, component tree, file tree, targeted diff, mermaid — or builds a self-contained interactive HTML page with background, intuition, a code walkthrough and a quiz, saved as a dated file outside the repository.
---

# Explain Diff

Two modes:

- **Quick view** — answer in chat with the smallest visual that makes the point. Default for "show me", "explain this", "what changed here".
- **Full page** — one self-contained HTML file. Use when the user asks for a page, artifact, walkthrough, quiz, or something to share.

Unclear? Give the quick view and offer the page in one line.

## Investigate first

Source of truth is the checkout, diff, branch, PR, or files the user named; if the target is ambiguous, pick the likeliest and say so. Trace the old and new paths through callers, tests, and data models until you can explain behavior rather than file-by-file edits. Never claim behavior the source does not show; separate observed fact from interpretation.

## Views

Pick by what you are explaining, not by habit. Every non-trivial claim about structure or flow gets a view — prose alone is the failure mode.

| Explaining                                      | View                | Shape                                                                |
| ----------------------------------------------- | ------------------- | -------------------------------------------------------------------- |
| an algorithm, a branch, a state machine         | pseudocode          | `on(save)` / `if unchanged` / `return cached`                        |
| what calls what at runtime                      | call tree           | indented function names, one per line                                |
| UI structure, where state lives                 | component tree      | `<Page>` with hooks and children indented, file path in parens       |
| where responsibility lives, a refactor's layout | file tree           | `src/` with `# what it owns` per entry                               |
| a value's journey between systems               | labeled flow        | boxes with the payload named on each arrow                           |
| what changed, when the shape already exists     | diff                | shape-matched: diff the call tree, the file tree, the component tree |
| two behaviors worth comparing                   | before/after panels | same fields on both sides, so the delta is scannable                 |
| mappings, invariants, edge cases, toy data      | table               | one row per case                                                     |
| a definition, invariant, or consequence         | callout             | one paragraph                                                        |
| interaction across processes over time          | mermaid sequence    | chat only — the page has no network, so build it as a labeled flow   |

Rules for every view:

- Keep only the calls, files, props, and boundaries the current question needs. Trim the rest.
- Label arrows with the data that moves, and use real values from the code (`"cad"`, not `value`).
- Put each view next to the one or two sentences it supports, never in a gallery.
- Show the whole block only when most of it is new, order or ownership would otherwise be hidden, or the user needs a copyable target shape.
- Never ASCII box-art. Text-shape sketches in `<pre><code>` are structure and are welcome; drawn boxes are not.

<important if="you are producing the full HTML explanation page">

## Full page

Build the narrative first: what forced the change, how it behaved before, the smallest mental model of the new behavior, how the code realizes it, what the edges and trade-offs are.

Then one self-contained HTML file — CSS and JS inline, no fonts, CDNs, images, packages, or network. Save it outside the repo as `/tmp/YYYY-MM-DD-explanation-<slug>.html` with today's date.

Sections, in order, linked from a table of contents:

1. **Background** — only the system the change touches. Optional beginner mental model, then the exact components, contracts, and prior behavior.
2. **Intuition** — the idea before the implementation, on small concrete toy inputs. Old vs new where it clarifies.
3. **Code** — conceptual groups in execution or dependency order, never file order. Precise file and line references, never the whole diff. **Each group opens with a view from the table** — the call tree, component tree, file tree, or diff that group changes — then prose explains it.
4. **Edges** — a table of what happens at each edge, and a callout for each invariant.
5. **Quiz** — exactly five interactive multiple-choice questions.

Also: a file tree if the change moves responsibility between directories; a component tree if it touches UI.

Plain language, jargon explained on first use, readable on phones, one continuous page with no top-level tabs.

Before handing off, confirm the file is a complete HTML document with no external dependencies and working quiz interactions; open or inspect it if practical. Return the absolute path as a clickable local-file link, say what you inspected, and name any assumption or unverified claim. Keep the file out of the repository unless asked.
</important>

<important if="you are styling the HTML page">

## Styling

The page carries its own stylesheet inline, as the first thing in `<style>` — never a `<link>`, never a file beside the output. Copy the token block and element rules from one of the pages in `examples/` so every page looks like the same document, then add a handful of page-specific rules after it.

Define colors once as tokens (`--brand`, `--ink`, `--ink-2`, `--line`, `--panel`, `--code-bg`, `--ok`, `--no`) under `color-scheme: light dark` and use them everywhere; no new colors, gradients, or shadows. Only system font stacks — no fetched or embedded fonts.

The element vocabulary covers the views: `.callout`, `.card.before` / `.card.after`, `.flow` with `.step` and labeled `.arrow`, `.grid` of `.card`, `.tablewrap`, `pre` (which must set `white-space: pre` or `pre-wrap`), and `.quiz`.
</important>

<important if="you are writing the five quiz questions">

## Quiz

Ask about behavior, causality, contracts, edges, or trade-offs — never a phrase copied off the page. Medium difficulty. Clicking an option immediately reveals whether it was right and why, including the code path.

- Shuffle options per question and spread the correct positions across the five. Position, length, letter, punctuation, or phrasing must never hint at the answer.
- Keep options comparable in length, grammar, specificity, and confidence.
- Every distractor is a real misunderstanding of this change. No jokes, no impossibilities, no "all of the above", nothing unanswerable from the page.
- Keep answers and explanations in the page's JS data so it works offline. Reveal only after selection; mark the choice, explain the right reasoning and the misconception behind the wrong one.
- Nothing may leak the answer before selection — not styling, DOM order, labels, `title`, or accessibility text.
  </important>

<important if="you are writing HTML, code blocks, or inline JavaScript into the page">

## HTML constraints

- Escape code-derived text for HTML and JS contexts; preserve meaningful whitespace.
- Code blocks are `<pre><code>...</code></pre>`; verify whitespace survives in the saved file.
- Keep JS small, namespaced, dependency-free. Event listeners over inline handlers; no fragile global selectors across repeated quiz cards.
- Visible focus states, sufficient contrast, and no meaning carried by color alone.
  </important>

<important if="you are writing a full HTML page and have not yet seen one">

## Examples

`examples/` holds two real pages produced by this skill, both explaining MIT-licensed open-source code. Read one first for shape, not content:

- `examples/2026-09-08-explanation-p-limit-reject-on-clear.html` — a single-commit feature explanation (`sindresorhus/p-limit`, commit `8907801f`).
- `examples/2026-09-08-explanation-express-router-dispatch.html` — a multi-file subsystem explanation (`pillarjs/router` v2.2.0, three files).

They use the view table densely and carry their own inlined CSS; take yours from either one.
</important>
