#!/usr/bin/env python3
"""Run consistent GitHub issue inspection and creation workflows through gh."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPTS_DIR = Path(__file__).resolve().parent


class SkillError(Exception):
    def __init__(self, reason: str, remediation: str, details: str = "") -> None:
        self.reason = reason
        self.remediation = remediation
        self.details = details
        super().__init__(reason)


def print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def run_json(command: list[str], reason: str, remediation: str) -> Any:
    result = run(command)
    if result.returncode != 0:
        raise SkillError(reason, remediation, result.stderr.strip())
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SkillError(reason, remediation, str(exc)) from exc


def readiness() -> None:
    result = run([sys.executable, str(SCRIPTS_DIR / "gh_readiness.py")])
    if result.returncode == 0:
        return
    try:
        status = json.loads(result.stdout)
    except json.JSONDecodeError:
        status = {}
    raise SkillError(
        str(status.get("reason", "gh_not_ready")),
        str(status.get("remediation", "Run: gh auth login")),
    )


def resolve_repository(repo: str | None) -> dict[str, Any]:
    return run_json(
        [
            "gh",
            "repo",
            "view",
            *([repo] if repo else []),
            "--json",
            "nameWithOwner,defaultBranchRef,viewerPermission,url",
        ],
        "repository_not_accessible",
        "Specify an accessible repository with --repo OWNER/REPO.",
    )


def template_mode(repo_dir: str) -> dict[str, Any]:
    return run_json(
        [sys.executable, str(SCRIPTS_DIR / "template_mode.py"), "--repo", repo_dir],
        "template_check_failed",
        "Check that --repo-dir points to a readable local directory.",
    )


def existing_labels(repo: str) -> set[str]:
    labels = run_json(
        ["gh", "label", "list", "--repo", repo, "--limit", "1000", "--json", "name"],
        "label_lookup_failed",
        "Verify repository access and label permissions.",
    )
    return {label["name"] for label in labels}


def context(repo: str | None, repo_dir: str) -> tuple[dict[str, Any], dict[str, Any]]:
    readiness()
    repository = resolve_repository(repo)
    templates = template_mode(repo_dir)
    return repository, templates


def inspect(args: argparse.Namespace) -> int:
    repository, templates = context(args.repo, args.repo_dir)
    labels = existing_labels(repository["nameWithOwner"])
    print_json(
        {
            "operation": "inspect",
            "ready": True,
            "repository": repository,
            "template_mode": templates["template_mode"],
            "template_warnings": templates["warnings"],
            "label_count": len(labels),
        }
    )
    return 0


def create_command(args: argparse.Namespace, repository: str) -> list[str]:
    command = [
        "gh",
        "issue",
        "create",
        "--repo",
        repository,
        "--title",
        args.title,
        "--body-file",
        str(Path(args.body_file).resolve()),
    ]
    for label in args.label:
        command.extend(["--label", label])
    for assignee in args.assignee:
        command.extend(["--assignee", assignee])
    if args.milestone:
        command.extend(["--milestone", args.milestone])
    return command


def create(args: argparse.Namespace) -> int:
    body_file = Path(args.body_file)
    if not body_file.is_file():
        raise SkillError(
            "body_file_not_found",
            "Pass an existing Markdown file with --body-file.",
            str(body_file),
        )

    repository, templates = context(args.repo, args.repo_dir)
    repo_name = repository["nameWithOwner"]
    requested_labels = set(args.label)
    missing_labels = sorted(requested_labels - existing_labels(repo_name))
    if missing_labels:
        raise SkillError(
            "unknown_labels",
            "Create the labels first or remove them from --label.",
            ", ".join(missing_labels),
        )

    command = create_command(args, repo_name)
    preview = {
        "operation": "create",
        "dry_run": not args.apply,
        "repository": repo_name,
        "template_mode": templates["template_mode"],
        "template_warnings": templates["warnings"],
        "requested": {
            "title": args.title,
            "body_file": str(body_file),
            "labels": args.label,
            "assignees": args.assignee,
            "milestone": args.milestone,
        },
        "command": command,
    }
    if not args.apply:
        print_json(preview)
        return 0

    result = run(command)
    if result.returncode != 0:
        raise SkillError(
            "issue_create_failed",
            "Review the preview, permissions, and requested issue fields before retrying.",
            result.stderr.strip(),
        )

    issue_url = result.stdout.strip()
    issue = run_json(
        [
            "gh",
            "issue",
            "view",
            issue_url,
            "--repo",
            repo_name,
            "--json",
            "number,title,state,labels,assignees,milestone,url",
        ],
        "issue_verification_failed",
        "Re-read the created issue with gh issue view and verify its fields.",
    )
    preview.update({"dry_run": False, "issue": issue})
    preview.pop("command")
    print_json(preview)
    return 0


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect a GitHub repository or create an issue with a preview by default."
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect gh readiness, repository, templates, and labels.")
    inspect_parser.add_argument("--repo", help="GitHub repository in OWNER/REPO form; defaults to the current repository.")
    inspect_parser.add_argument("--repo-dir", default=".", help="Local target repository for template inspection (default: current directory).")
    inspect_parser.set_defaults(handler=inspect)

    create_parser = subparsers.add_parser("create", help="Preview an issue creation; use --apply to create it.")
    create_parser.add_argument("--repo", help="GitHub repository in OWNER/REPO form; defaults to the current repository.")
    create_parser.add_argument("--repo-dir", default=".", help="Local target repository for template inspection (default: current directory).")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--body-file", required=True, help="Path to the Markdown issue body.")
    create_parser.add_argument("--label", action="append", default=[], help="Existing label to apply; repeat for multiple labels.")
    create_parser.add_argument("--assignee", action="append", default=[], help="GitHub login to assign; repeat for multiple assignees.")
    create_parser.add_argument("--milestone")
    create_parser.add_argument("--apply", action="store_true", help="Create the issue. Omit for the safe dry-run default.")
    create_parser.set_defaults(handler=create)
    return parser


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except SkillError as error:
        print_json(
            {
                "ready": False,
                "reason": error.reason,
                "remediation": error.remediation,
                **({"details": error.details} if error.details else {}),
            }
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
