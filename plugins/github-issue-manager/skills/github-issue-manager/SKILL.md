---
name: github-issue-manager
description: Manage GitHub issues end-to-end with the gh CLI. Use when Codex needs to inspect, create, triage, edit, assign, label, comment on, close, reopen, delete, or create work branches for GitHub issues; when asked to turn requirements or bugs into GitHub issues; when asked to manage issue templates under .github/ISSUE_TEMPLATE; or when asked to connect issue work to branches or pull requests.
---

# GitHub Issue Manager

## Operating rule

Automatically determine whether to use repository issue templates before creating issues. Run `scripts/template_mode.py --repo <target-repo>` after resolving the target repository.

- When `template_mode.enabled` is `true`, map the request to a detected usable template and use it.
- When it is `false`, do not block the requested issue operation: create or manage the issue without template mapping, and report that template mode was disabled.
- Treat malformed YAML forms as unusable. Report their warnings; do not silently select them.
- Create or repair templates only when the user explicitly asks, or when the requested issue workflow specifically requires templates.

Use the authenticated `gh` CLI for every GitHub operation. Use `git remote get-url origin` and `gh repo view --json nameWithOwner` to infer the repository when the user does not specify one.

## gh CLI readiness

1. Run `python3 <skill-path>/scripts/gh_readiness.py` before every GitHub operation.
2. If it exits non-zero, report its JSON `reason` and `remediation`, then stop. Do not run any `gh`, GitHub, branch, or issue mutation command.
3. Run `gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef,viewerPermission,url` before mutations to verify repository and permission.
4. Prefer built-in `gh issue`, `gh label`, `gh repo`, and `gh pr` commands.
5. Use `gh api` only when a needed GitHub operation has no built-in `gh` command. Keep the request scoped to the target repository and report the endpoint or GraphQL operation used.

Read `references/backend-selection.md` when choosing between built-in `gh` commands and `gh api`.

## Safety levels

Execute directly:
- Read/list/search issues, labels, milestones, assignees, templates, and branches.
- Draft issue bodies and preview mutations.
- Create a single issue when title/body/repo are clear and templates are present.
- Add a non-destructive comment to a specific issue when the user explicitly asks.

Preview before execution:
- Editing title/body/labels/assignees/milestones/type/project fields.
- Closing or reopening issues.
- Creating local or remote branches from issues.
- Creating or changing issue templates.
- Creating multiple issues from a batch.

Require explicit confirmation:
- Deleting issues or comments.
- Bulk edits affecting more than 5 issues.
- Removing labels, assignees, milestones, or project fields.
- Pushing a branch to remote or changing protected/default branches.

Treat issue deletion as permanent and permission-limited. Prefer closing with a rationale comment unless the user explicitly requests deletion.

## Core workflow

1. Resolve repository.
   - Prefer explicit `owner/repo` in the request.
   - Else infer from the current git remote.
   - Verify with `gh repo view`.
2. Detect template mode.
   - Run `python3 <skill-path>/scripts/template_mode.py --repo <target-repo>`.
   - Use templates only when `template_mode.enabled` is `true`.
   - When disabled, proceed without template mapping and include the reason in the final report.
   - Read `references/issue-template-policy.md` only when creating, repairing, or validating template files.
3. Select the `gh` operation.
   - Prefer a built-in `gh` command; use `gh api` only when required.
   - Keep raw command output or tool results for verification.
4. Preview risky mutations.
   - Show target repo, issue numbers, changed fields, labels/assignees/milestones, branch name, and close/delete impact.
5. Execute.
   - Use smallest scoped command/tool call.
   - Avoid mixing unrelated mutations in one step.
6. Verify.
   - Re-read the issue, branch, labels, or template after mutation.
   - Report URL, issue number, branch name, changed fields, and remaining risks.

## Issue title policy

Use concrete open-source style work titles. Do not use bracket prefixes such as `[FEATURE]`, `[BUG]`, or `[MAINTENANCE]`.

Preferred formats:
- `<area>: <action>`
- When useful, conventional style: `feat(area): <action>` or `fix(area): <action>`

Keep issue type, status, priority, and canonical service/area classification in labels or GitHub Project fields, not bracket prefixes in the title. Any `<area>` in the title is only a concise work surface hint, not the authoritative classification.

Apply this policy whenever passing `--title` to `gh issue create` or `scripts/gh_issue.py create`. `scripts/gh_issue.py` accepts the title as provided; do not rely on automatic title normalization unless explicitly requested in the future. Do not rely on issue template frontmatter defaults such as `title: "[FEATURE] "`; replace them with a policy-compliant title before creation.

Good examples:
- `matching-engine: emit executions through worker output channel`
- `etl: ingest raw match logs`
- `ci: add minimal Go quality gate`
- `docs: document exchange-lab topology`
- `fix(orderbook): remove stale maker index`

Bad examples:
- `[FEATURE] Add execution events`
- `[BUG] Matching is broken`
- `[MAINTENANCE] Refactor repository`

## Supported tasks

For standard repository inspection and single-issue creation, prefer `scripts/gh_issue.py`. It runs the `gh` readiness gate, checks the target repository and local template mode, validates requested labels, defaults to dry-run, and verifies created issues. Use direct `gh` commands for operations not implemented by the script.

```bash
python3 <skill-path>/scripts/gh_issue.py inspect --repo OWNER/REPO --repo-dir /path/to/local/repo
python3 <skill-path>/scripts/gh_issue.py create --repo OWNER/REPO --repo-dir /path/to/local/repo --title "matching-engine: emit executions through worker output channel" --body-file /tmp/issue.md --label bug
# Create only after reviewing the preview:
python3 <skill-path>/scripts/gh_issue.py create --repo OWNER/REPO --repo-dir /path/to/local/repo --title "matching-engine: emit executions through worker output channel" --body-file /tmp/issue.md --label bug --apply
```

### Issue discovery and triage

Support listing, filtering, searching duplicates, summarizing, prioritizing, and grouping issues by label, assignee, milestone, project, state, type, and age.

Useful `gh` fallbacks:

```bash
gh issue list --repo OWNER/REPO --state open --limit 50 --json number,title,state,labels,assignees,milestone,updatedAt,url
gh issue view NUMBER --repo OWNER/REPO --comments --json number,title,body,state,labels,assignees,milestone,comments,url
```

### Issue creation

When template mode is enabled, map the request to an existing template, but replace any template-provided bracket-prefix title default with a title that follows the Issue title policy. When disabled, create a structured body directly from the request; include acceptance criteria for tasks/features and reproduction details for bugs. Do not propose templates unless the user asks for them or the workflow requires them.

Useful `gh` fallback:

```bash
gh issue create --repo OWNER/REPO --title "ci: add minimal Go quality gate" --body-file /tmp/issue-body.md --label "label1,label2" --assignee "login" --milestone "MILESTONE"
```

### Issue editing and assignment

Manage title, body, labels, assignees, milestone, issue type, project fields, and comments. For removals, preview first. Use `gh api` only for operations unsupported by built-in `gh` commands.

Useful `gh` fallbacks:

```bash
gh issue edit NUMBER --repo OWNER/REPO --title "TITLE" --body-file /tmp/body.md --add-label "bug" --add-assignee "login"
gh issue comment NUMBER --repo OWNER/REPO --body-file /tmp/comment.md
gh issue close NUMBER --repo OWNER/REPO --comment "Closing because ..."
gh issue reopen NUMBER --repo OWNER/REPO --comment "Reopening because ..."
```

### Issue deletion

Delete only after explicit confirmation and permission check. Verify whether the authenticated account has admin/owner permission. Prefer a close comment instead of deletion when deletion is not necessary.

### Branch creation from an issue

Before creating a branch, read `references/branch-naming-policy.md` and inspect `.github/github-issue-manager.yml` in the target repository. Use the configuration when present; otherwise use the default `issue/{number}-{slug}` pattern. Never create a configuration file unless the user asks to configure branch naming.

Show the active branch configuration before branch creation: configuration source (request, repository file, or default), matched label and prefix, generated name, base branch, and whether remote push is enabled. A branch name explicitly supplied in the current request overrides repository configuration for that request only.

Default branch names are:

```text
issue/<number>-<slug>
fix/<number>-<slug>
feat/<number>-<slug>
docs/<number>-<slug>
```

Default to local branch creation unless the user requests a remote branch. Link work back to the issue through branch name, PR body keywords, or issue comments.

Useful fallback:

```bash
git fetch origin
git switch -c issue/NUMBER-short-slug origin/DEFAULT_BRANCH
# Optional only after preview/confirmation:
git push -u origin issue/NUMBER-short-slug
gh issue comment NUMBER --repo OWNER/REPO --body "Work started on branch \`issue/NUMBER-short-slug\`."
```

## Template-mode detector

Use the bundled detector against the **target repository**, not the skill repository:

```bash
python3 <skill-path>/scripts/template_mode.py --repo /path/to/target-repo
```

It emits JSON. `template_mode.enabled` is `true` only when at least one Markdown template or YAML issue form is usable. Missing templates or invalid-only YAML forms set it to `false`; this disables template mapping but does not prevent issue operations.

Read `references/issue-template-policy.md` before creating or editing `.github/ISSUE_TEMPLATE` files. Read `references/backend-selection.md` for backend-specific capabilities and caveats.

## Branch configuration

Read `references/branch-naming-policy.md` before creating branches or creating/editing `.github/github-issue-manager.yml`. Use that file as the supported configuration schema and resolution order.

## Reporting format

For completed mutations, report:

- Repository
- Operation performed
- Issue URL(s)
- Changed fields
- Branch name and whether it is local or pushed
- For branch operations: configuration source, selected prefix, and base branch
- Verification command/tool result
- Any permission or API caveats
