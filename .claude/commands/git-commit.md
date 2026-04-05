# Git Commit

Analyze changes and create a commit with an appropriate message, then push to remote.

## Instructions

1. Run `git status` to see all modified, added, and deleted files
2. Run `git diff` to see the actual changes in tracked files
3. Run `git diff --cached` to see any already-staged changes
4. Run `git log --oneline -5` to understand the commit message style used in this repository
5. Based on the changes, create a concise and descriptive commit message that:
   - Uses imperative mood (e.g., "Add feature" not "Added feature")
   - Summarizes what changed and why
   - Follows the repository's existing commit message conventions
6. Stage all changes with `git add -A`
7. Create the commit with the generated message
8. Push to the remote repository with `git push`

If the push fails due to remote changes, inform the user and suggest running `git pull --rebase` first.
