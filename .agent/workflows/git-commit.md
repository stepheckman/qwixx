---
description: Stage all changes and generate a conventional commit message.
---

1. Run `git status` to see what is currently staged and unstaged.
2. If there are no changes at all, stop and inform the user.
3. If there are changes but nothing is staged, run `git add .` to stage everything.
4. Run `git diff --cached` to get the changes to be committed.
5. Analyze the diffs and generate a concise, conventional commit message (e.g., `feat: add login page`, `fix: update dependency`). The message should be under 50 characters for the subject line.
6. Propose the commit command: `git commit -m "your generated message"`.
