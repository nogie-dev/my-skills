# gh CLI Workflow

## Command selection

1. Use built-in `gh` commands for standard issue, label, repository, and pull request operations.
2. Use `gh api` only when the built-in command set lacks an operation or required field.
3. Do not use `curl` or another GitHub client as a fallback.

## Capability notes

- GitHub issue comments are managed through issue comment endpoints/tools. Pull requests are also issues for shared operations such as labels, assignees, and milestones.
- Issue deletion is permanent and permission-limited. Closing with a rationale comment is safer and should be proposed first.
- Issue forms live under `.github/ISSUE_TEMPLATE/` as YAML files. Template chooser config lives at `.github/ISSUE_TEMPLATE/config.yml`.
- GitHub supports creating a branch for an issue from the issue page. In CLI workflows, create a normal git branch using an issue-derived name and link it with a PR body or issue comment.

## Readiness checklist

Run the readiness gate before every GitHub operation. It returns exit code `0` only when `gh` is installed and authenticated; otherwise it returns `1` and JSON remediation. Stop on failure.

```bash
python3 <skill-path>/scripts/gh_readiness.py
```

Before mutation, also run:

```bash
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef,viewerPermission,url
gh issue view NUMBER --repo OWNER/REPO --json number,title,state,url
```

Prefer JSON output for reads and exact flags for writes. Store long bodies in temp files and pass `--body-file` to avoid shell quoting problems.

## `gh api` checklist

Use `gh api` only when the operation is unsupported by a built-in `gh` command. Confirm token scope and repository permission before mutation. Keep REST paths and GraphQL variables scoped to the target repository. Record the endpoint or GraphQL operation in the final report.
