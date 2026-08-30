# Code Archaeology (git + in-repo)

Use this source first. It connects the target directly to the commits, pull requests, comments, tests, documents, and related files that shaped it.

## Search

```bash
# Full history of the file through renames
git log --follow --oneline -- <file>

# Commits that added or removed an exact string
git log -S '<exact_string_from_code>' -- <file>

# Commits matching a pattern
git log -G '<regex>' -- <file>

# Who wrote each line and when
git blame -L <start>,<end> <file>

# Full diff of a commit
git show <hash>

# Commits between two points affecting this file
git log <old>..<new> -p -- <file>
```

For substantive commits, find linked PRs and read their bodies, reviews, comments, and issues:

```bash
git log -1 --format=%B <hash>
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews,files
```

Also check nearby TODOs, ADRs, changelogs, release notes, and tests. Test names and assertions often reveal the edge cases that motivated a change.

## Evidence

Prefer explicit explanations of the problem, constraint, tradeoff, or incident. An inline comment is evidence only when it states intent; code shape alone is not.

## Pitfalls

- Squash merges may hide branch commits; use the PR body and discussion.
- Commit messages can be misleading; inspect the diff.
- Copied patterns may have no intentional rationale; trace their origin.
- Bot commits and automated backports rarely explain motivation.
- A temporal or textual match is supporting evidence, not proof of causation.

## Return

For each relevant commit, PR, comment, test, or document, report the exact text or a faithful paraphrase, its hash/number/path, author/date when available, and whether it is direct or circumstantial evidence.
