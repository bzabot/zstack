import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    values = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key] = value.strip().strip("\"'")
    return values


class PackageTests(unittest.TestCase):
    def test_manifest_and_migrated_paths(self):
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "zstack")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["author"]["name"], "Bruno Zabot")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest)
        self.assertTrue((SKILLS / "zabot-mode/SKILL.md").is_file())
        self.assertTrue((SKILLS / "comment-sicko/SKILL.md").is_file())
        self.assertFalse((ROOT / "zabot-mode").exists())
        self.assertFalse((ROOT / "agents/comment-sicko.md").exists())

    def test_hooks_capture_the_supported_lifecycle_synchronously(self):
        config = json.loads((ROOT / "hooks/hooks.json").read_text())
        hooks = config["hooks"]
        expected = {
            "SessionStart",
            "UserPromptSubmit",
            "PreToolUse",
            "PostToolUse",
            "SubagentStart",
            "SubagentStop",
            "Stop",
            "SessionEnd",
        }
        self.assertEqual(set(hooks), expected)
        command = 'python3 "${PLUGIN_ROOT}/hooks/zabot_trace.py" record'
        for event_name, matchers in hooks.items():
            self.assertEqual(len(matchers), 1)
            entries = matchers[0]["hooks"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["type"], "command")
            self.assertEqual(entries[0]["command"], command)
            self.assertNotIn("async", entries[0])
            if event_name == "SessionEnd":
                self.assertLessEqual(entries[0]["timeout"], 3)

    def test_skill_names_are_unique_kebab_case_and_match_their_directory(self):
        names = []
        for directory in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
            metadata = frontmatter(directory / "SKILL.md")
            name = metadata.get("name")
            self.assertIsNotNone(name, directory)
            self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertEqual(name, directory.name)
            names.append(name)
        self.assertEqual(len(names), len(set(names)))

    def test_unsupported_frontmatter_is_replaced_by_explicit_invocation_policy(self):
        explicit_only = {
            "architect",
            "create-verification-skill",
            "interrogate",
            "no-comments",
            "tdd",
            "zabot-mode",
            *{
                path.name
                for path in SKILLS.glob("principle-*")
                if path.is_dir()
            },
        }
        for skill in sorted(explicit_only):
            text = (SKILLS / skill / "SKILL.md").read_text()
            self.assertNotIn("disable-model-invocation", text, skill)
            policy = (SKILLS / skill / "agents/openai.yaml").read_text()
            self.assertIn("allow_implicit_invocation: false", policy, skill)

    def test_obsolete_delegation_and_verification_vocabulary_is_absent(self):
        offenders = {
            "subagent_type",
            "generalPurpose",
            "`readonly`",
            "readonly:",
            "Opus",
            "Haiku",
            ".zabot/skills",
        }
        for path in sorted(SKILLS.rglob("*.md")):
            text = path.read_text()
            for obsolete in offenders:
                self.assertNotIn(obsolete, text, f"{obsolete!r} in {path}")

    def test_zabot_mode_directly_links_every_principle(self):
        text = (SKILLS / "zabot-mode/SKILL.md").read_text()
        principle_dirs = sorted(path.name for path in SKILLS.glob("principle-*"))
        for name in principle_dirs:
            link = f"[**{name}**](../{name}/SKILL.md)"
            self.assertIn(link, text)
            self.assertTrue((SKILLS / "zabot-mode" / f"../{name}/SKILL.md").resolve().is_file())

    def test_architect_and_playbooks_use_resolvable_exact_principle_links(self):
        paths = [SKILLS / "architect/SKILL.md", *sorted((SKILLS / "zabot-mode/playbooks").glob("*.md"))]
        for path in paths:
            text = path.read_text()
            for target in re.findall(r"\]\((\.\./(?:\.\./)?principle-[a-z-]+/SKILL\.md)\)", text):
                self.assertTrue((path.parent / target).resolve().is_file(), f"{path}: {target}")
            without_links = re.sub(
                r"\[\*\*principle-[a-z-]+\*\*\]\(\.\./(?:\.\./)?principle-[a-z-]+/SKILL\.md\)",
                "",
                text,
            )
            bare = re.findall(r"\bprinciple-[a-z-]+\b", without_links)
            self.assertEqual(bare, [], f"unlinked principle name(s) in {path}: {bare}")

    def test_todo_order_and_tracing_reference_are_explicit(self):
        text = (SKILLS / "zabot-mode/SKILL.md").read_text()
        first = text.index("first todo item")
        playbook = text.index("matched playbook's steps")
        self.assertLess(first, playbook)
        self.assertIn("references/tracing.md", text)


if __name__ == "__main__":
    unittest.main()
