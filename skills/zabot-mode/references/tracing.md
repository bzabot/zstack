# Observable tracing

Zstack records what Codex exposes to plugin hooks: hook inputs, agent identifiers and transcript references, prompts, final messages, and supported tool calls and results. It does not expose or reconstruct private chain-of-thought. Treat explicit `Decision rationale` summaries as the auditable explanation of a child's choice.

Once the plugin hooks are enabled and trusted, they observe every Codex session in which the plugin is active, not only turns that explicitly invoke `$zabot-mode`. Disable the plugin hooks when you do not want local capture.

Each hook invocation creates one immutable JSON event under `$PLUGIN_DATA/traces/v1/sessions/<session>/events/`. `trace.jsonl` is a deterministic chronological projection. `tree.json` is the machine-readable recursive agent tree. `tree.md` is the review view. Stop events replace those three projections by scanning the immutable events; the projections are not capture-time sources of truth.

Secret-like fields are recursively redacted. Oversized strings are replaced with a preview, SHA-256 digest, and original byte count. This is defense in depth, not a guarantee: prompts, paths, tool results, and unknown fields may still contain sensitive data under unexpected names. Keep `$PLUGIN_DATA` private, inspect before sharing, and apply repository-specific redaction where needed.

Coverage is limited to events delivered to these hooks. The tracer does not parse transcript files and does not claim visibility into hosted tools or hidden model reasoning. Missing start, stop, or tool-result events are preserved as incomplete or orphan warnings rather than guessed into a complete story.
