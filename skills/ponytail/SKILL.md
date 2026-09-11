---
name: ponytail
description: Forces the smallest coding solution that fully works. Use when the user asks for Ponytail, a minimal solution, less code, YAGNI, or help avoiding over-engineering.
license: MIT
---

# Ponytail

Use the least code and complexity that solves the actual coding task. Lazy means efficient, not careless.

Ponytail applies to the current task only. `full` is the default. Use `/ponytail lite`, `/ponytail full`, or `/ponytail ultra` when the user chooses a level. Stop applying it when the task ends or the user says `stop ponytail` or `normal mode`.

## Decision ladder

Stop at the first rung that solves the real problem:

1. Does this need to exist? Skip speculative work and say so.
2. Does the codebase already contain the helper, type, or pattern? Reuse it.
3. Does the standard library solve it?
4. Does the platform already solve it?
5. Does an installed dependency solve it? Do not add a dependency for a small amount of code.
6. Can the solution be one line?
7. Write the minimum code that remains.

Read the task and the code it touches before using the ladder. A small diff in the wrong place is not a lazy solution. For bugs, inspect all callers and fix the shared root cause rather than patching one named path.

## Rules

- Do not add abstractions, configuration, wrappers, or scaffolding without a present need.
- Prefer deletion and reuse over addition.
- Keep the call hierarchy flat and state local.
- Choose the standard library or a native feature before a new dependency.
- Mark a deliberate simplification with a `ponytail:` comment when it has a real, known ceiling and an obvious upgrade trigger.
- Do not remove validation at trust boundaries, error handling that prevents data loss, security controls, accessibility basics, or anything the user explicitly requested.
- The spec remains the floor. Ponytail can simplify the implementation, but it cannot silently remove a requirement.

## Intensity

- `lite`: Build what was asked and mention one simpler alternative.
- `full`: Apply the ladder and ship the shortest complete implementation.
- `ultra`: Challenge speculative requirements and prefer deletion before addition.

Non-trivial logic needs one runnable check. Use the smallest useful test, assertion, demo, or command. Trivial one-liners do not need a new test.

## Output

Lead with the result. Unless the user asks for a report, keep the explanation to what was skipped and when it should be added.
