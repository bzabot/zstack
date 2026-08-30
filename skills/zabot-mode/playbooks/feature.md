### Feature

**You own the design. Plan, review, verify.** Delegate implementation; stay in the lead.

1. `how` over the affected subsystem.
2. `architect` for parallel design exploration. Skipping stays as `architect skipped: <reason>`; do not fold the design decision silently into implementation.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target with [**principle-separate-before-serializing-shared-state**](../../principle-separate-before-serializing-shared-state/SKILL.md). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. Delegate code-writing to a worker with a unique `task_name` and a specific scope: file paths, success criteria, and the named organizing structure from [**principle-model-the-domain**](../../principle-model-the-domain/SKILL.md), chosen before the delegate writes logic. Inherit the parent model by default; set `model` and `reasoning_effort` only when the work needs an explicit override. A state machine beats scattered booleans, a table or registry beats branching, and a typed model beats repeated shape assumptions. When the implementation admits multiple valid shapes, name the choice explicitly, such as error handling, abstraction layer, or test structure. Review the diff yourself. Mandatory: no skip-with-reason escape, and [**principle-laziness-protocol**](../../principle-laziness-protocol/SKILL.md) does not override it because the gain is review separation, not lines saved. You can spawn a subagent even though you are one; "the app is small" and "a subagent cannot spawn one" are both wrong. A subagent forbidden to spawn satisfies this by owning the diff directly with the same review separation; no "standing by" reply that waits on a nested agent. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit liberally.
5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass; flag it.
6. Rebase into small, ordered commits; stack follow-ups.
   Use [**principle-sequence-verifiable-units**](../../principle-sequence-verifiable-units/SKILL.md), building, verifying, and committing each small unit before the next.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline; that owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries; spawn a fresh owner rather than chaining interrupts.

**Reply:** what you built, what you chose and why, open decisions. Tables for design alternatives.
