# Issue Template Policy

## Required repository structure

Accept either:

```text
.github/ISSUE_TEMPLATE.md
```

or the preferred multi-template structure:

```text
.github/ISSUE_TEMPLATE/
├── bug_report.yml
├── feature_request.yml
├── task.yml
└── config.yml
```

Prefer YAML issue forms for new repositories because they support required fields, labels, assignees, and structured inputs.

## Minimum templates

### Bug report

Require:
- Summary
- Environment
- Steps to reproduce
- Expected result
- Actual result
- Logs/screenshots if relevant
- Regression status

Default labels: `bug`, optionally component/priority labels.

### Feature request

Require:
- Problem or user need
- Proposed outcome
- Acceptance criteria
- Alternatives considered
- Scope exclusions

Default labels: `enhancement` or `feature`.

### Task

Require:
- Goal
- Context
- Checklist
- Acceptance criteria
- Test/verification plan

Default labels: `task`.

## Validation checklist

For YAML issue forms, check:
- Top-level `name` exists.
- Top-level `description` exists.
- Top-level `body` exists and is a list.
- Required user inputs use `validations.required: true` where needed.
- Default labels exist or are intentionally new.
- Assignees are valid GitHub logins before relying on them.

## Template creation behavior

When templates are missing, propose the minimum three-template set. Preview file paths and content before writing unless the user explicitly asked to create templates immediately.
