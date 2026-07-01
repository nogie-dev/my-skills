#!/usr/bin/env python3
"""Block GitHub Project operations until gh is installed, authenticated, and project-capable."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def emit(ready: bool, reason: str, remediation: str, **extra: object) -> int:
    print(json.dumps({"ready": ready, "reason": reason, "remediation": remediation, **extra}, ensure_ascii=False))
    return 0 if ready else 1


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", help="Optional GitHub user/org login to verify project access against")
    args = parser.parse_args()

    gh = shutil.which("gh")
    if not gh:
        return emit(False, "gh_not_installed", "Install GitHub CLI, then run: gh auth login")

    try:
        status = run([gh, "auth", "status"])
    except (OSError, subprocess.TimeoutExpired):
        return emit(False, "gh_auth_check_failed", "Check gh/network, then run: gh auth login")

    if status.returncode != 0:
        return emit(False, "gh_not_authenticated", "Authenticate GitHub CLI, then run: gh auth login")

    viewer = run([gh, "api", "user", "--jq", ".login"])
    login = viewer.stdout.strip() if viewer.returncode == 0 else None

    probe = [gh, "project", "list", "--limit", "1", "--format", "json"]
    if args.owner:
        probe += ["--owner", args.owner]
    access = run(probe)
    if access.returncode != 0:
        msg = (access.stderr or access.stdout).strip()
        return emit(
            False,
            "project_scope_or_access_missing",
            "Grant project scope with: gh auth refresh -s project; also verify owner/project permissions",
            owner=args.owner,
            login=login,
            detail=msg[-500:],
        )

    return emit(True, "ready", "", owner=args.owner, login=login)


if __name__ == "__main__":
    sys.exit(main())
