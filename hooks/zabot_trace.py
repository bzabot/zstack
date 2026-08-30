#!/usr/bin/env python3
"""Capture immutable Codex hook events and derive reviewable agent trees."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVENT_SCHEMA = "dev.zabot.trace-event/v1"
TREE_SCHEMA = "dev.zabot.agent-tree/v1"
MAX_STRING_BYTES = 16 * 1024
SECRET_KEY = re.compile(
    r"(?:api[-_]?key|access[-_]?key|authorization|cookie|credential|passwd|password|private[-_]?key|secret|session[-_]?token|token)$",
    re.IGNORECASE,
)


def _safe_component(value: Any) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", str(value or "unknown-session"))
    safe = safe.strip(".")
    return safe[:160] or "unknown-session"


def _secure_directories(path: Path, data_root: Path) -> None:
    missing = []
    current = path
    while current != data_root and not current.exists():
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir(mode=0o700, exist_ok=True)
    current = path
    while current != data_root:
        os.chmod(current, 0o700)
        current = current.parent


def _cap_string(value: str) -> str | dict[str, Any]:
    encoded = value.encode("utf-8")
    if len(encoded) <= MAX_STRING_BYTES:
        return value
    preview_bytes = encoded[:MAX_STRING_BYTES]
    preview = preview_bytes.decode("utf-8", errors="ignore")
    return {
        "__zabot_truncated__": True,
        "preview": preview,
        "original_bytes": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def redact(value: Any, key: str = "") -> Any:
    if SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(child_key): redact(child, str(child_key)) for child_key, child in value.items()}
    if isinstance(value, list):
        return [redact(child) for child in value]
    if isinstance(value, str):
        return _cap_string(value)
    return value


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_bytes(path, (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())


def _atomic_bytes(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_name, path)
        os.chmod(path, 0o600)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def _hook_name(payload: dict[str, Any]) -> str:
    return str(payload.get("hook_event_name") or payload.get("hook_event") or "Unknown")


def record_event(payload: dict[str, Any], plugin_data: str | Path) -> tuple[dict[str, Any], Path]:
    if not isinstance(payload, dict):
        raise TypeError("hook input must be a JSON object")
    data_root = Path(plugin_data)
    session_id = str(payload.get("session_id") or "unknown-session")
    event_id = uuid.uuid4().hex
    observed_at = str(payload.get("observed_at") or datetime.now(timezone.utc).isoformat())
    actor_ref = str(payload.get("transcript_path") or "root")
    envelope_keys = {
        "hook_event_name",
        "hook_event",
        "session_id",
        "turn_id",
        "model",
        "permission_mode",
        "observed_at",
    }
    codex_event = redact({key: value for key, value in payload.items() if key not in envelope_keys})
    envelope = {
        "schema": EVENT_SCHEMA,
        "event_id": event_id,
        "observed_at": observed_at,
        "hook_event": _hook_name(payload),
        "session_id": session_id,
        "turn_id": payload.get("turn_id"),
        "actor_ref": actor_ref,
        "model": payload.get("model"),
        "permission_mode": payload.get("permission_mode"),
        "codex_event": codex_event,
    }
    event_dir = data_root / "traces" / "v1" / "sessions" / _safe_component(session_id) / "events"
    _secure_directories(event_dir, data_root)
    event_path = event_dir / f"{event_id}.json"
    _atomic_json(event_path, envelope)
    return envelope, event_path


def _events(session_dir: Path) -> list[dict[str, Any]]:
    events = []
    for path in (session_dir / "events").glob("*.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if value.get("schema") == EVENT_SCHEMA:
            events.append(value)
    return sorted(events, key=lambda item: (str(item.get("observed_at", "")), str(item.get("event_id", ""))))


def _new_node(
    actor_ref: str,
    agent_id: str | None = None,
    agent_type: str = "root",
    created_at: str = "",
) -> dict[str, Any]:
    return {
        "agent_id": agent_id,
        "agent_type": agent_type,
        "actor_ref": actor_ref,
        "transcript_ref": actor_ref if actor_ref != "root" else None,
        "model": None,
        "permission_mode": None,
        "prompts": [],
        "final_messages": [],
        "tool_calls": [],
        "warnings": [],
        "children": [],
        "_created_at": created_at,
    }


def _first_root_ref(events: list[dict[str, Any]], child_refs: set[str]) -> str:
    preferred = {"SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"}
    for item in events:
        actor = str(item.get("actor_ref") or "root")
        if item.get("hook_event") in preferred and actor != "root" and actor not in child_refs:
            return actor
    for item in events:
        actor = str(item.get("actor_ref") or "root")
        if item.get("hook_event") in preferred and actor not in child_refs:
            return actor
    for item in events:
        actor = str(item.get("actor_ref") or "root")
        if actor != "root" and actor not in child_refs:
            return actor
    return "root"


def _event_value(item: dict[str, Any], *keys: str) -> Any:
    payload = item.get("codex_event") or {}
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def reconstruct_tree(events: list[dict[str, Any]]) -> dict[str, Any]:
    stops = {
        str(_event_value(item, "agent_id")): str(_event_value(item, "agent_transcript_path"))
        for item in events
        if item.get("hook_event") == "SubagentStop"
        and _event_value(item, "agent_id") is not None
        and _event_value(item, "agent_transcript_path") is not None
    }
    child_refs = set(stops.values())
    root_ref = _first_root_ref(events, child_refs)
    root = _new_node(root_ref)
    nodes_by_ref = {root_ref: root}
    nodes_by_id: dict[str, dict[str, Any]] = {}
    parents: dict[str, str] = {}
    global_warnings: list[str] = []

    for item in events:
        if item.get("hook_event") != "SubagentStart":
            continue
        agent_id_value = _event_value(item, "agent_id")
        if agent_id_value is None:
            global_warnings.append(f"incomplete SubagentStart event: {item.get('event_id')}")
            continue
        agent_id = str(agent_id_value)
        actor_ref = stops.get(agent_id, f"agent:{agent_id}")
        node = _new_node(
            actor_ref,
            agent_id,
            str(_event_value(item, "agent_type") or "worker"),
            str(item.get("observed_at") or ""),
        )
        node["model"] = item.get("model")
        node["permission_mode"] = item.get("permission_mode")
        prompt = _event_value(item, "prompt")
        if prompt is not None:
            node["prompts"].append(prompt)
        if agent_id not in stops:
            node["warnings"].append(f"incomplete agent: {agent_id} has no SubagentStop")
        nodes_by_id[agent_id] = node
        nodes_by_ref[actor_ref] = node
        parents[agent_id] = str(item.get("actor_ref") or root_ref)

    for agent_id, node in sorted(nodes_by_id.items(), key=lambda pair: (pair[1]["_created_at"], pair[0])):
        parent_ref = parents[agent_id]
        parent = nodes_by_ref.get(parent_ref)
        if parent is None:
            warning = f"orphan agent: {agent_id} has unknown parent {parent_ref}"
            node["warnings"].append(warning)
            global_warnings.append(warning)
            parent = root
        parent["children"].append(node)

    orphan_nodes: dict[str, dict[str, Any]] = {}

    def node_for(item: dict[str, Any]) -> dict[str, Any]:
        actor = str(item.get("actor_ref") or root_ref)
        node = nodes_by_ref.get(actor)
        if node is not None:
            return node
        node = orphan_nodes.get(actor)
        if node is None:
            warning = f"orphan actor: {actor} has no SubagentStart correlation"
            node = _new_node(actor, agent_type="orphan", created_at=str(item.get("observed_at") or ""))
            node["warnings"].append(warning)
            orphan_nodes[actor] = node
            global_warnings.append(warning)
            root["children"].append(node)
        return node

    tool_calls: dict[tuple[str, str], dict[str, Any]] = {}
    for item in events:
        hook = item.get("hook_event")
        node = node_for(item)
        if node["model"] is None and item.get("model") is not None:
            node["model"] = item["model"]
        if node["permission_mode"] is None and item.get("permission_mode") is not None:
            node["permission_mode"] = item["permission_mode"]
        if hook == "UserPromptSubmit":
            prompt = _event_value(item, "prompt", "user_prompt")
            if prompt is not None:
                node["prompts"].append(prompt)
        elif hook == "Stop":
            message = _event_value(item, "last_assistant_message")
            if message is not None:
                node["final_messages"].append(message)
        elif hook == "SubagentStop":
            agent_id_value = _event_value(item, "agent_id")
            child = nodes_by_id.get(str(agent_id_value)) if agent_id_value is not None else None
            if child is None:
                warning = f"orphan SubagentStop: {agent_id_value or item.get('event_id')}"
                global_warnings.append(warning)
            else:
                message = _event_value(item, "last_assistant_message")
                if message is not None:
                    child["final_messages"].append(message)
        elif hook == "PreToolUse":
            call_id = str(_event_value(item, "tool_use_id") or item.get("event_id"))
            call = {
                "tool_use_id": call_id,
                "tool_name": _event_value(item, "tool_name"),
                "input": _event_value(item, "tool_input"),
                "result": None,
                "warnings": [],
                "_created_at": str(item.get("observed_at") or ""),
            }
            node["tool_calls"].append(call)
            tool_calls[(node["actor_ref"], call_id)] = call
        elif hook == "PostToolUse":
            call_id = str(_event_value(item, "tool_use_id") or item.get("event_id"))
            call = tool_calls.get((node["actor_ref"], call_id))
            if call is None:
                warning = f"tool result without call: {call_id}"
                call = {
                    "tool_use_id": call_id,
                    "tool_name": _event_value(item, "tool_name"),
                    "input": None,
                    "result": _event_value(item, "tool_response", "tool_result"),
                    "warnings": [warning],
                    "_created_at": str(item.get("observed_at") or ""),
                }
                node["tool_calls"].append(call)
                node["warnings"].append(warning)
            else:
                call["result"] = _event_value(item, "tool_response", "tool_result")

    def finish(node: dict[str, Any]) -> None:
        node["children"].sort(key=lambda child: (child["_created_at"], child["actor_ref"]))
        node["tool_calls"].sort(key=lambda call: (call["_created_at"], call["tool_use_id"]))
        for call in node["tool_calls"]:
            if call["result"] is None:
                warning = f"incomplete tool call: {call['tool_use_id']}"
                call["warnings"].append(warning)
                node["warnings"].append(warning)
            call.pop("_created_at", None)
        for child in node["children"]:
            finish(child)
        node.pop("_created_at", None)

    finish(root)
    return {
        "schema": TREE_SCHEMA,
        "session_id": events[0].get("session_id") if events else None,
        "root": root,
        "warnings": sorted(set(global_warnings)),
    }


def _inline(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def render_markdown(tree: dict[str, Any]) -> str:
    lines = ["# Zabot trace", ""]
    if tree.get("warnings"):
        lines.extend(["## Trace warnings", ""])
        lines.extend(f"- {warning}" for warning in tree["warnings"])
        lines.append("")

    def render(node: dict[str, Any], depth: int) -> None:
        label = "root" if node.get("agent_id") is None and node.get("agent_type") == "root" else node.get("agent_id") or node.get("agent_type")
        lines.extend([f"{'#' * min(depth + 2, 6)} Agent: {label}", ""])
        for key in ("agent_type", "model", "permission_mode", "transcript_ref"):
            if node.get(key) is not None:
                lines.append(f"- {key.replace('_', ' ').title()}: {_inline(node[key])}")
        for prompt in node.get("prompts", []):
            lines.append(f"- Prompt: {_inline(prompt)}")
        for message in node.get("final_messages", []):
            lines.append(f"- Final message: {_inline(message)}")
        for warning in node.get("warnings", []):
            lines.append(f"- Warning: {warning}")
        for call in node.get("tool_calls", []):
            lines.append(f"- Tool {call.get('tool_name') or 'unknown'} ({call['tool_use_id']})")
            lines.append(f"  - Input: {_inline(call.get('input'))}")
            lines.append(f"  - Result: {_inline(call.get('result'))}")
            for warning in call.get("warnings", []):
                lines.append(f"  - Warning: {warning}")
        lines.append("")
        for child in node.get("children", []):
            render(child, depth + 1)

    render(tree["root"], 0)
    return "\n".join(lines).rstrip() + "\n"


def build_projections(session_dir: str | Path) -> dict[str, Any]:
    session_path = Path(session_dir)
    events = _events(session_path)
    tree = reconstruct_tree(events)
    trace = b"".join(
        (json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        for item in events
    )
    _atomic_bytes(session_path / "trace.jsonl", trace)
    _atomic_json(session_path / "tree.json", tree)
    _atomic_bytes(session_path / "tree.md", render_markdown(tree).encode())
    return tree


def record_cli() -> int:
    payload = json.load(sys.stdin)
    plugin_data = os.environ.get("PLUGIN_DATA")
    if not plugin_data:
        raise RuntimeError("PLUGIN_DATA is required")
    envelope, event_path = record_event(payload, plugin_data)
    hook = envelope["hook_event"]
    if hook in {"Stop", "SessionEnd"}:
        build_projections(event_path.parent.parent)
    if hook == "Stop":
        print(json.dumps({"systemMessage": f"Zabot trace: {event_path.parent.parent / 'tree.md'}"}))
    elif hook == "SubagentStop":
        print("{}")
    return 0


def main(argv: list[str]) -> int:
    if argv != ["record"]:
        print("usage: zabot_trace.py record", file=sys.stderr)
        return 2
    return record_cli()


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        print(f"zabot trace error: {error}", file=sys.stderr)
        raise SystemExit(1)
