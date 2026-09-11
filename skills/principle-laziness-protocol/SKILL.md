---
name: principle-laziness-protocol
description: "Apply when sequencing an addition, refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. Subtract first, then build the smallest change that solves the problem, measured by the load it puts on the next reader."
---

# Laziness Protocol

Writing code is cheap for you, which makes over-engineering easy. Counter it by borrowing a human maintainer's fatigue. Aim for the most result with the least code and complexity.

**The spec is the floor, not the ceiling.** This principle governs how you build what the spec asks for. It never authorizes building less than it asks for. A table, an endpoint, or a limit the spec names is not speculative, and the spec has usually already argued for it. If a spec'd element genuinely does not earn its place, say so out loud and build it anyway pending an answer. Silently shipping the smaller thing is the failure mode this principle is most likely to cause.

## Subtract first

Removal gives you a simpler base, which makes the next addition smaller and less brittle. Adding to a complex system compounds complexity; cutting first reveals the essential structure and usually makes the design obvious.

- Sequence removal before construction. Delete dead weight, redundant validators, and orphan references before introducing the new shape.
- Cut before you polish. Reach the minimum before investing in quality.
- Design for observed usage, not speculative edge cases. No validators, parsers, or guards beyond what the spec demands.
- Out-of-spec features drag validators behind them. Persistence, retry-on-startup, and schema migration each need guards to defend their inputs.
- When a reference has no novel content, delete it rather than leaving a stub.
- Leave the design slightly simpler behind the same or smaller surface than you found it.

## Then build the smallest thing

- **Prefer deletion.** Asked to refactor or improve, look for removals before additions.
- **Minimize the diff.** The smallest change that solves the problem. Fewer lines beat elegant boilerplate.
- **Maintain a flat call hierarchy.** If answering a question requires tracing through more than 3 files or layers, flatten it. A rich interface that hides substantial work is not a deep call chain.
- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag.
- **Question the threading.** If a task asks you to pass a new signal through types, schemas, pipelines, or similar layers, stop and look for a more direct path.
- **Sweat the small leaks.** Remove tiny pass-throughs, representation leaks, and duplicated choices before they spread. Small leaks compound into permanent coordination costs.

## Measure it as reader load

LOC and cyclomatic complexity are proxies. The thing that matters is the work a reader must do. Two independent axes:

1. **Layers to trace.** How many indirections sit between the question and the answer.
2. **State to hold.** How much hidden or mutable context the reader must keep in their head.

A flat file with 50 globals is as hard to reason about as a 6-layer adapter stack. Guard both.

- **Collapse layers that do not earn their keep:** wrappers with one caller, adapters with no second implementation, indirection introduced for a future that never came. Inline them.
- **Make adjacent layers change the abstraction.** A layer that repeats the same methods and arguments adds reader load without compression.
- **Demand interface compression.** A broad interface that hides little complexity makes readers learn both the surface and the implementation. Prefer boundaries that hide meaningful decisions.
- **Shrink state scope:** pure functions over mutations, locals over fields, fields over module state, module state over globals. Derive instead of sync.
- **Name the invariant at the boundary,** not in every consumer, so the reader learns it once.
- Before adding a layer or a piece of state, ask whether it reduces reader load somewhere else by at least as much.

**The test:** can a new reader answer "where does X come from?" and "what can change X?" in under 30 seconds? If not, cut layers or cut state.

**Prime directive:** if a human developer would find the code exhausting to maintain, it is a bad solution. Be lazy. Stay simple.
