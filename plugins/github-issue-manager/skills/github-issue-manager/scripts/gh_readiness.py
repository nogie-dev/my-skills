#!/usr/bin/env python3
"""Block GitHub issue operations until the gh CLI is installed and authenticated."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


def result(ready: bool, reason: str, remediation: str) -> int:
    print(
        json.dumps(
            {
                "ready": ready,
                "reason": reason,
                "remediation": remediation,
            },
            ensure_ascii=False,
        )
    )
    return 0 if ready else 1


def main() -> int:
    gh = shutil.which("gh")
    if gh is None:
        return result(
            False,
            "gh_not_installed",
            "Install GitHub CLI, then run: gh auth login",
        )

    try:
        status = subprocess.run(
            [gh, "auth", "status"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return result(
            False,
            "gh_auth_check_failed",
            "Check the gh installation and network, then run: gh auth login",
        )

    if status.returncode != 0:
        return result(
            False,
            "gh_not_authenticated",
            "Authenticate GitHub CLI, then run: gh auth login",
        )

    return result(True, "ready", "")


if __name__ == "__main__":
    sys.exit(main())
