# Branch Naming Policy

## Configuration file

Read `.github/github-issue-manager.yml` in the target repository before creating an issue branch. The file is optional. If it is absent, use `issue/{number}-{slug}` and do not create a configuration file unless the user asks.

```yaml
branch_naming:
  default_prefix: issue
  prefixes:
    bug: fix
    feature: feat
    task: chore
  prefix_priority: [bug, feature, task]
  format: "{prefix}/{number}-{slug}"
  slug:
    max_length: 48
    separator: "-"
    lowercase: true
  base_branch: default
  create_remote: false
  comment_on_issue: false
```

## Resolution order

1. Use a branch name directly supplied in the current request.
2. Otherwise, read `branch_naming` from the repository configuration.
3. Select the first matching issue label in `prefix_priority`; use `default_prefix` when none matches.
4. If no configuration exists, use the built-in default `issue/{number}-{slug}`.

Use a label's final segment when matching `type/bug`, `kind/bug`, or `bug`; `type/bug` therefore matches `bug`. Do not infer a prefix from issue title text.

## Format and safety

- Allow only `{prefix}`, `{number}`, and `{slug}` placeholders in `format`.
- Normalize `slug` to lowercase when configured, replace runs of non-alphanumeric characters with `separator`, trim separators, and apply `max_length`.
- Use `default` in `base_branch` to mean the repository default branch.
- Treat `create_remote` and `comment_on_issue` as opt-in. Preview both before execution.
- Stop and show alternatives if the resulting local or remote branch already exists.
- Report the configuration source, chosen label/prefix, generated branch name, base branch, and push status before creating a branch.

## Configuration changes

Create or edit the configuration only after showing the target path and proposed YAML. Keep unknown keys unchanged. If required keys have invalid types or the format uses unsupported placeholders, do not create a branch from the configuration; explain the problem and fall back only with the user's approval.
