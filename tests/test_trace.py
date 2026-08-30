import concurrent.futures
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "hooks/zabot_trace.py"


def load_trace_module():
    spec = importlib.util.spec_from_file_location("zabot_trace", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def event(hook_event, observed_at, transcript_path="/tmp/root.jsonl", **extra):
    return {
        "hook_event_name": hook_event,
        "session_id": "session-1",
        "turn_id": "turn-1",
        "transcript_path": transcript_path,
        "observed_at": observed_at,
        **extra,
    }


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_trace_module()
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_one_input_creates_one_event_and_preserves_unknown_fields(self):
        payload = event("UserPromptSubmit", "2026-01-01T00:00:00Z", prompt="hello", future_field={"x": 1})
        envelope, path = self.trace.record_event(payload, self.data)
        files = list(path.parent.glob("*.json"))
        self.assertEqual(files, [path])
        stored = json.loads(path.read_text())
        self.assertEqual(stored, envelope)
        self.assertEqual(stored["schema"], "dev.zabot.trace-event/v1")
        self.assertEqual(stored["hook_event"], "UserPromptSubmit")
        self.assertEqual(stored["actor_ref"], "/tmp/root.jsonl")
        self.assertEqual(stored["codex_event"]["future_field"], {"x": 1})

    def test_redaction_payload_cap_hash_and_permissions(self):
        secret = "do-not-store"
        oversized = "é" * (self.trace.MAX_STRING_BYTES + 10)
        _, path = self.trace.record_event(
            event(
                "PreToolUse",
                "2026-01-01T00:00:00Z",
                api_key=secret,
                nested={"Authorization": secret, "safe": "kept", "large": oversized},
            ),
            self.data,
        )
        stored = json.loads(path.read_text())
        self.assertEqual(stored["codex_event"]["api_key"], "[REDACTED]")
        self.assertEqual(stored["codex_event"]["nested"]["Authorization"], "[REDACTED]")
        marker = stored["codex_event"]["nested"]["large"]
        encoded = oversized.encode()
        self.assertTrue(marker["__zabot_truncated__"])
        self.assertEqual(marker["original_bytes"], len(encoded))
        self.assertEqual(marker["sha256"], hashlib.sha256(encoded).hexdigest())
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        current = path.parent
        while current != self.data:
            self.assertEqual(stat.S_IMODE(current.stat().st_mode), 0o700, current)
            current = current.parent

    def test_concurrent_recorders_create_distinct_complete_files(self):
        payloads = [event("PreToolUse", f"2026-01-01T00:00:{i:02d}Z", tool_use_id=str(i)) for i in range(20)]
        env = {**os.environ, "PLUGIN_DATA": str(self.data)}

        def run(payload):
            return subprocess.run(
                [sys.executable, str(SCRIPT), "record"],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(run, payloads))
        self.assertTrue(all(result.returncode == 0 for result in results), results)
        event_dir = self.data / "traces/v1/sessions/session-1/events"
        files = list(event_dir.iterdir())
        self.assertEqual(len(files), len(payloads))
        self.assertEqual(len({path.name for path in files}), len(payloads))
        for path in files:
            self.assertEqual(path.suffix, ".json")
            json.loads(path.read_text())


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_trace_module()
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_nested_events(self):
        inputs = [
            event("SubagentStop", "2026-01-01T00:00:07Z", agent_id="grand", agent_transcript_path="/tmp/grand.jsonl", last_assistant_message="grand final"),
            event("PostToolUse", "2026-01-01T00:00:05Z", "/tmp/child.jsonl", tool_use_id="call-1", tool_response={"ok": True}),
            event("SubagentStart", "2026-01-01T00:00:03Z", "/tmp/child.jsonl", agent_id="grand", agent_type="worker", prompt="inspect leaf", model="gpt-leaf", permission_mode="read-only instruction"),
            event("UserPromptSubmit", "2026-01-01T00:00:00Z", prompt="root prompt", model="gpt-root", permission_mode="workspace-write"),
            event("SubagentStart", "2026-01-01T00:00:01Z", agent_id="child", agent_type="explorer", prompt="inspect subsystem", model="gpt-child", permission_mode="read-only"),
            event("PreToolUse", "2026-01-01T00:00:04Z", "/tmp/child.jsonl", tool_use_id="call-1", tool_name="rg", tool_input={"query": "needle"}),
            event("PreToolUse", "2026-01-01T00:00:06Z", "/tmp/grand.jsonl", tool_use_id="incomplete", tool_name="read", tool_input={"path": "x"}),
            event("SubagentStop", "2026-01-01T00:00:08Z", agent_id="child", agent_transcript_path="/tmp/child.jsonl", last_assistant_message="child final"),
            event("Stop", "2026-01-01T00:00:09Z", last_assistant_message="root final"),
            event("PostToolUse", "2026-01-01T00:00:02Z", "/tmp/orphan.jsonl", tool_use_id="orphan-call", tool_response="unknown actor"),
        ]
        for payload in inputs:
            self.trace.record_event(payload, self.data)
        return self.data / "traces/v1/sessions/session-1"

    def test_shuffled_nested_events_reconstruct_deterministically(self):
        session_dir = self.write_nested_events()
        first = self.trace.build_projections(session_dir)
        first_json = (session_dir / "tree.json").read_bytes()
        first_md = (session_dir / "tree.md").read_bytes()
        second = self.trace.build_projections(session_dir)
        self.assertEqual(first, second)
        self.assertEqual(first_json, (session_dir / "tree.json").read_bytes())
        self.assertEqual(first_md, (session_dir / "tree.md").read_bytes())
        root = first["root"]
        self.assertEqual(root["actor_ref"], "/tmp/root.jsonl")
        self.assertEqual(root["model"], "gpt-root")
        self.assertEqual(root["permission_mode"], "workspace-write")
        self.assertEqual(root["prompts"], ["root prompt"])
        self.assertEqual(root["final_messages"], ["root final"])
        child = root["children"][0]
        grand = child["children"][0]
        self.assertEqual((child["agent_id"], child["agent_type"], child["actor_ref"]), ("child", "explorer", "/tmp/child.jsonl"))
        self.assertEqual((grand["agent_id"], grand["agent_type"], grand["actor_ref"]), ("grand", "worker", "/tmp/grand.jsonl"))
        self.assertEqual(child["prompts"], ["inspect subsystem"])
        self.assertEqual(child["final_messages"], ["child final"])
        self.assertEqual(grand["final_messages"], ["grand final"])

    def test_tool_correlation_and_incomplete_orphan_warnings(self):
        tree = self.trace.build_projections(self.write_nested_events())
        child = tree["root"]["children"][0]
        grand = child["children"][0]
        call = child["tool_calls"][0]
        self.assertEqual(call["tool_use_id"], "call-1")
        self.assertEqual(call["tool_name"], "rg")
        self.assertEqual(call["input"], {"query": "needle"})
        self.assertEqual(call["result"], {"ok": True})
        self.assertIn("incomplete tool call: incomplete", grand["warnings"])
        self.assertTrue(any("orphan actor" in warning for warning in tree["warnings"]))

    def test_json_and_markdown_include_observable_agent_details(self):
        session_dir = self.write_nested_events()
        tree = self.trace.build_projections(session_dir)
        markdown = (session_dir / "tree.md").read_text()
        for value in [
            "gpt-root",
            "workspace-write",
            "explorer",
            "gpt-child",
            "inspect subsystem",
            "child final",
            "/tmp/child.jsonl",
            "rg",
            "needle",
            "incomplete tool call",
            "orphan actor",
        ]:
            self.assertIn(value, markdown)
        self.assertEqual(tree["schema"], "dev.zabot.agent-tree/v1")

    def test_cli_stop_emits_json_and_writes_projections(self):
        env = {**os.environ, "PLUGIN_DATA": str(self.data)}
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "record"],
            input=json.dumps(event("Stop", "2026-01-01T00:00:00Z", last_assistant_message="done")),
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertIn("systemMessage", response)
        self.assertIn("tree.md", response["systemMessage"])
        session_dir = self.data / "traces/v1/sessions/session-1"
        for name in ["trace.jsonl", "tree.json", "tree.md"]:
            self.assertTrue((session_dir / name).is_file(), name)

    def test_cli_subagent_stop_emits_valid_json(self):
        env = {**os.environ, "PLUGIN_DATA": str(self.data)}
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "record"],
            input=json.dumps(event("SubagentStop", "2026-01-01T00:00:00Z", agent_id="a", agent_transcript_path="/tmp/a.jsonl")),
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsInstance(json.loads(result.stdout), dict)


if __name__ == "__main__":
    unittest.main()
