#!/usr/bin/env python3
"""Report whether a target repository has usable GitHub issue templates."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FORM_EXTENSIONS = {".yml", ".yaml"}
MARKDOWN_EXTENSIONS = {".md"}


def git_root(path: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return path.resolve()
    return Path(result.stdout.strip()).resolve()


def form_warnings(path: Path) -> list[str]:
    """Perform dependency-free checks for the required issue-form keys."""
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["cannot read as UTF-8"]
    except OSError as exc:
        return [str(exc)]

    warnings = []
    for key in ("name", "description", "body"):
        if not re.search(rf"(?m)^{key}\s*:", content):
            warnings.append(f"missing top-level '{key}:'")
    return warnings


def inspect(repo: Path) -> dict[str, object]:
    root = git_root(repo)
    template_dir = root / ".github" / "ISSUE_TEMPLATE"
    legacy_template = root / ".github" / "ISSUE_TEMPLATE.md"
    templates: list[dict[str, object]] = []

    if template_dir.is_dir():
        for path in sorted(template_dir.iterdir()):
            if not path.is_file() or path.name == "config.yml":
                continue
            suffix = path.suffix.lower()
            if suffix not in FORM_EXTENSIONS | MARKDOWN_EXTENSIONS:
                continue
            warnings = form_warnings(path) if suffix in FORM_EXTENSIONS else []
            templates.append(
                {
                    "path": str(path.relative_to(root)),
                    "kind": "form" if suffix in FORM_EXTENSIONS else "markdown",
                    "warnings": warnings,
                }
            )

    if legacy_template.is_file():
        templates.append(
            {"path": str(legacy_template.relative_to(root)), "kind": "markdown", "warnings": []}
        )

    usable = [template for template in templates if not template["warnings"]]
    warnings = [
        f"{template['path']}: {warning}"
        for template in templates
        for warning in template["warnings"]
    ]

    return {
        "repository_root": str(root),
        "template_mode": {
            "enabled": bool(usable),
            "reason": (
                "usable issue template found"
                if usable
                else "no usable issue template found; create issues without template mapping"
            ),
        },
        "templates": templates,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect whether GitHub issue templates should be used for a repository."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository or directory to inspect (default: current directory).",
    )
    args = parser.parse_args()
    print(json.dumps(inspect(Path(args.repo)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
