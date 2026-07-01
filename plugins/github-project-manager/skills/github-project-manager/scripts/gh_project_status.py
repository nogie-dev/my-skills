#!/usr/bin/env python3
"""Resolve GitHub Projects IDs and update a single-select Status-like field."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def fail(reason: str, remediation: str, **extra: object) -> int:
    print(json.dumps({"ok": False, "reason": reason, "remediation": remediation, **extra}, ensure_ascii=False))
    return 1


def out(**data: object) -> int:
    print(json.dumps({"ok": True, **data}, ensure_ascii=False))
    return 0


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, check=False)


def gh_json(cmd: list[str]) -> Any:
    p = run(cmd)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip())
    return json.loads(p.stdout or "{}")


def norm(s: object) -> str:
    return str(s or "").casefold().strip()


def one(matches: list[dict[str, Any]], kind: str, hint: str) -> dict[str, Any]:
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise LookupError(f"no {kind} matched {hint!r}")
    names = [m.get("title") or m.get("name") or m.get("id") for m in matches[:10]]
    raise LookupError(f"multiple {kind}s matched {hint!r}: {names}")


def project(gh: str, owner: str, project_ref: str) -> dict[str, Any]:
    if project_ref.isdigit():
        return gh_json([gh, "project", "view", project_ref, "--owner", owner, "--format", "json"])
    data = gh_json([gh, "project", "list", "--owner", owner, "--limit", "100", "--format", "json"])
    return one([p for p in data.get("projects", []) if norm(p.get("title")) == norm(project_ref)], "project", project_ref)


def field(gh: str, owner: str, project_number: str, field_name: str) -> dict[str, Any]:
    data = gh_json([gh, "project", "field-list", project_number, "--owner", owner, "--limit", "100", "--format", "json"])
    f = one([x for x in data.get("fields", []) if norm(x.get("name")) == norm(field_name)], "field", field_name)
    if "options" not in f:
        raise LookupError(f"field {field_name!r} is not a single-select field")
    return f


def option(field_obj: dict[str, Any], option_name: str) -> dict[str, Any]:
    return one([o for o in field_obj.get("options", []) if norm(o.get("name")) == norm(option_name)], "option", option_name)


def item(gh: str, owner: str, project_number: str, item_ref: str, repo: str | None, limit: str) -> dict[str, Any]:
    data = gh_json([gh, "project", "item-list", project_number, "--owner", owner, "--limit", limit, "--format", "json"])
    items = data.get("items", [])
    if item_ref.startswith("PVTI_"):
        return one([i for i in items if i.get("id") == item_ref], "item", item_ref)
    if item_ref.startswith("http"):
        return one([i for i in items if i.get("content", {}).get("url") == item_ref], "item", item_ref)
    if repo and item_ref.isdigit():
        return one([i for i in items if str(i.get("content", {}).get("number")) == item_ref and norm(i.get("content", {}).get("repository")) == norm(repo)], "item", f"{repo}#{item_ref}")
    needle = norm(item_ref)
    return one([i for i in items if needle in norm(i.get("title") or i.get("content", {}).get("title"))], "item", item_ref)


def main() -> int:
    ap = argparse.ArgumentParser(description="Set a GitHub Project item's Status/single-select field. Dry-run by default.")
    ap.add_argument("--owner", required=True)
    ap.add_argument("--project", required=True, help="Project number or exact title")
    ap.add_argument("--item", required=True, help="Item ID, issue/PR URL, title substring, or issue number with --repo")
    ap.add_argument("--repo", help="OWNER/REPO when --item is an issue/PR number")
    ap.add_argument("--status", required=True, help="Target option name, e.g. 'In progress'")
    ap.add_argument("--field", default="Status")
    ap.add_argument("--limit", default="200")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    gh = shutil.which("gh")
    if not gh:
        return fail("gh_not_installed", "Install GitHub CLI, then run: gh auth login")

    ready_script = Path(__file__).with_name("gh_project_readiness.py")
    ready = run([sys.executable, str(ready_script), "--owner", args.owner])
    if ready.returncode != 0:
        return fail("not_ready", "Fix gh readiness first", detail=(ready.stdout or ready.stderr).strip())

    try:
        p = project(gh, args.owner, args.project)
        number = str(p["number"])
        f = field(gh, args.owner, number, args.field)
        opt = option(f, args.status)
        it = item(gh, args.owner, number, args.item, args.repo, args.limit)
    except (KeyError, LookupError, RuntimeError, json.JSONDecodeError) as e:
        return fail("resolve_failed", "Check owner, project, item, field, option, and item-list limit", detail=str(e))

    cmd = [gh, "project", "item-edit", "--project-id", p["id"], "--id", it["id"], "--field-id", f["id"], "--single-select-option-id", opt["id"]]
    preview = {
        "owner": args.owner,
        "project": {"number": p["number"], "title": p.get("title"), "id": p["id"], "url": p.get("url")},
        "item": {"id": it["id"], "title": it.get("title") or it.get("content", {}).get("title"), "url": it.get("content", {}).get("url")},
        "field": {"name": f["name"], "id": f["id"]},
        "option": {"name": opt["name"], "id": opt["id"]},
        "command": " ".join(cmd),
    }
    if not args.apply:
        return out(dry_run=True, **preview)

    applied = run(cmd)
    if applied.returncode != 0:
        return fail("edit_failed", "Inspect gh project item-edit error", detail=(applied.stderr or applied.stdout).strip(), preview=preview)
    verify = item(gh, args.owner, number, it["id"], None, args.limit)
    return out(dry_run=False, verification={"status": verify.get(norm(args.field)) or verify.get(args.field.casefold()) or verify.get(args.field), "item_id": verify.get("id")}, **preview)


if __name__ == "__main__":
    sys.exit(main())
