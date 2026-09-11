---
name: grilling
description: Interview the user about a plan or coding idea, resolve its decisions, and write a final Markdown spec after confirmation.
---

# Grilling

Run an interview that stress-tests a plan, decision, or coding idea before implementation. Model the subject as a design tree. Each decision can open more decisions beneath it.

Grilling is explicit-only. Run it when the user asks for grilling or asks to turn an idea into a spec. Do not start implementation and do not invoke another implementation skill automatically.

## Rounds and frontier

Work in rounds. The frontier is every decision whose prerequisites are settled. Ask the whole current frontier in one round. Do not ask a question whose answer depends on another question still open in the same round. Recompute the frontier after the user answers.

Ask questions in this form:

```text
❓ **Q1** - **<question title>**: <question body>

➡️ <your recommended answer>
```

Number questions within each round. Recommendations must answer the question directly. The user owns decisions. Do not answer your own decision questions.

Facts are different from decisions. Inspect the repository, files, tools, and other available context when they can settle a fact. Ask the user only for choices that require their judgment. Keep unrelated questions in the current frontier moving while an environment check runs. Keep the coordinator at high reasoning for the tree and synthesis. Use fast explorers for routine fact collection, never for decisions.

Continue until the frontier is empty. The session is not complete merely because you have produced an outline. Ask the user to confirm that the understanding is shared. Do not write the spec or implement anything before that confirmation.

## Final spec

After confirmation, flatten the resolved discussion into a readable Markdown spec. Keep final decisions and concise rationale. Do not include the interview transcript, frontmatter, a status field, or a mandatory heading template. Follow the shape that fits the subject.

For a coding spec, preserve enough concrete detail for another agent to implement the current decision: intended behavior, scope, non-goals, relevant constraints, and how the result can be checked. Do not invent decisions that the user did not make.

Write only once, after confirmation. The default path is `specs/<slug>.md` in the current repository. Use an explicit output path when the user provides one. Do not overwrite an existing file unless the user clearly asks to replace it.

Report the path after writing. The user may discuss or edit the file before pointing `zabot-mode` at it. Grilling never starts implementation itself.
