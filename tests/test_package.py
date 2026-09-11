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
        self.assertEqual(manifest["version"], "0.2.0")
        self.assertEqual(manifest["author"]["name"], "Bruno Zabot")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest)
        self.assertEqual(manifest["interface"]["capabilities"], ["Skills"])
        self.assertTrue((SKILLS / "zabot-mode/SKILL.md").is_file())
        self.assertTrue((SKILLS / "comment-sicko/SKILL.md").is_file())
        self.assertFalse((ROOT / "zabot-mode").exists())
        self.assertFalse((ROOT / "agents/comment-sicko.md").exists())
        self.assertFalse((ROOT / "hooks/hooks.json").exists())
        self.assertFalse((ROOT / "hooks/zabot_trace.py").exists())

        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual((claude["name"], claude["version"]), ("zstack", "0.2.0"))
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(marketplace["plugins"][0]["source"], "./")

        codex_marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(codex_marketplace["plugins"][0]["source"], {"source": "local", "path": "./"})

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
            "create-verification-skill",
            "grilling",
            "ponytail",
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

    def test_zabot_mode_directly_links_ponytail(self):
        path = SKILLS / "zabot-mode/SKILL.md"
        text = path.read_text()
        self.assertIn("[**ponytail**](../ponytail/SKILL.md)", text)
        self.assertTrue((path.parent / "../ponytail/SKILL.md").resolve().is_file())

    def test_zabot_mode_uses_resolvable_exact_principle_links(self):
        path = SKILLS / "zabot-mode/SKILL.md"
        text = path.read_text()
        for target in re.findall(r"\]\((\.\./principle-[a-z-]+/SKILL\.md)\)", text):
            self.assertTrue((path.parent / target).resolve().is_file(), target)
        without_links = re.sub(
            r"\[\*\*principle-[a-z-]+\*\*\]\(\.\./principle-[a-z-]+/SKILL\.md\)",
            "",
            text,
        )
        bare = re.findall(r"\bprinciple-[a-z-]+\b", without_links)
        self.assertEqual(bare, [], f"unlinked principle name(s): {bare}")

    def test_no_skill_references_a_removed_skill(self):
        removed = ("architect", "how", "why", "interrogate", "tdd", "no-comments", "playbook")
        for path in sorted(SKILLS.rglob("*.md")):
            text = path.read_text()
            for name in removed:
                self.assertNotIn(f"]({name}/", text, f"{name} in {path}")
                self.assertNotIn(f"/{name}/SKILL.md", text, f"{name} in {path}")
                self.assertNotIn(f"/{name}`", text, f"{name} in {path}")

    def test_todo_order_is_explicit(self):
        text = (SKILLS / "zabot-mode/SKILL.md").read_text()
        first = text.index("first item")
        steps = text.index("Build steps copied verbatim")
        self.assertLess(first, steps)


if __name__ == "__main__":
    unittest.main()
