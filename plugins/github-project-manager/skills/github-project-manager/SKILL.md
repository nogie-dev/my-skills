---
name: github-project-manager
description: Manage GitHub Projects with the gh CLI. Use when Codex needs to list, inspect, create, edit, link, close, delete, copy, or manage GitHub Projects; add issues/PRs/draft items to projects; manage project fields; edit project item fields/status/priority; or summarize project state using gh project commands.
---

# GitHub Project Manager

## Readiness gate

Run before every GitHub Projects operation:

```bash
python3 <skill-path>/scripts/gh_project_readiness.py
python3 <skill-path>/scripts/gh_project_readiness.py --owner OWNER
```

If it exits non-zero, report its JSON `reason`, `remediation`, and `detail`, then stop. Do not run project mutations.

## Operating rule

Use the authenticated `gh` CLI. Prefer built-in `gh project` commands; use `gh api` only when `gh project` cannot do the operation.

## Safety levels

Execute directly:
- List/view projects, fields, items, linked repos/teams.

Preview before execution:
- Create/edit/close projects, add or archive items, edit item fields, create fields, link/unlink repos or teams.

Require explicit confirmation:
- Delete projects, fields, or items.
- Bulk edits affecting more than 5 items.

## Core workflow

1. Resolve owner: prefer explicit owner; else infer with `gh repo view --json owner,name` or current `gh` user.
2. Resolve project: use project number when provided; else `gh project list --owner OWNER` and match title.
3. Inspect current state before mutation.
4. Run the smallest scoped `gh project` command.
5. Verify by re-reading the changed project/item/field.
6. Report project URL, changed IDs/fields, verification command, and caveats.

## Status changes

For user requests like “move issue #4 to In progress”, use the helper instead of hand-resolving IDs. It resolves project ID, item ID, Status field ID, and option ID. It is dry-run by default.

```bash
python3 <skill-path>/scripts/gh_project_status.py --owner OWNER --project PROJECT_NUMBER_OR_TITLE --repo OWNER/REPO --item ISSUE_NUMBER --status "In progress"
python3 <skill-path>/scripts/gh_project_status.py --owner OWNER --project PROJECT_NUMBER_OR_TITLE --item ISSUE_OR_PR_URL --status Done
python3 <skill-path>/scripts/gh_project_status.py --owner OWNER --project PROJECT_NUMBER_OR_TITLE --item "title substring" --status Ready
```

After reviewing the JSON preview, apply with `--apply`. Use `--field FIELD_NAME` for other single-select fields such as Priority or Size.

## Useful commands

```bash
gh project list --owner OWNER --format json
gh project view PROJECT_NUMBER --owner OWNER --format json
gh project field-list PROJECT_NUMBER --owner OWNER --format json
gh project item-list PROJECT_NUMBER --owner OWNER --limit 100 --format json

gh project create --owner OWNER --title "TITLE"
gh project edit PROJECT_NUMBER --owner OWNER --title "TITLE"
gh project close PROJECT_NUMBER --owner OWNER
gh project delete PROJECT_NUMBER --owner OWNER

gh project item-add PROJECT_NUMBER --owner OWNER --url ISSUE_OR_PR_URL
gh project item-create PROJECT_NUMBER --owner OWNER --title "Draft title" --body "Draft body"
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --single-select-option-id OPTION_ID
gh project item-archive PROJECT_NUMBER --owner OWNER --id ITEM_ID
gh project item-delete PROJECT_NUMBER --owner OWNER --id ITEM_ID

gh project field-create PROJECT_NUMBER --owner OWNER --name "Field name" --data-type TEXT
gh project field-delete PROJECT_NUMBER --owner OWNER --id FIELD_ID

gh project link PROJECT_NUMBER --owner OWNER --repo OWNER/REPO
gh project unlink PROJECT_NUMBER --owner OWNER --repo OWNER/REPO
```
