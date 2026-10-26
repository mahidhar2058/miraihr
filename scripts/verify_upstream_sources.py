#!/usr/bin/env python3
"""Verify pinned upstream Git submodules and write JSON evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "deployment" / "dependencies.lock.json"
DEFAULT_REPORT = ROOT / "artifacts" / "upstream-source-verification.json"
LICENSE_NAME = re.compile(
    r"^(?:licen[cs]e|copying|notice|unlicense)(?:[.-].*)?$", re.IGNORECASE
)


class VerificationError(RuntimeError):
    """Raised when required repository metadata or evidence is missing."""


def git(args: list[str], *, cwd: Path = ROOT, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        raise VerificationError(
            f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def canonical_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if value.endswith(".git"):
        value = value[:-4]
    return value.casefold()


def load_sources() -> list[dict]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    sources: list[dict] = []
    for app in lock["applications"]:
        if app["name"] == "miraihr_core":
            continue
        name = app["name"]
        path = "india-payroll" if name == "india_payroll" else name
        sources.append(
            {
                "name": name,
                "path": f"upstream/{path}",
                "repository": app["repository"],
                "commit": app["commit"],
                "source_kind": "app",
                "license": app.get("license"),
            }
        )
    for name, path in (("frappe_docker", "frappe_docker"), ("frappe_helm", "helm")):
        entry = lock["deployment_sources"][name]
        sources.append(
            {
                "name": name,
                "path": f"upstream/{path}",
                "repository": entry["repository"],
                "commit": entry["commit"],
                "source_kind": "deployment",
                "license": entry.get("license"),
            }
        )
    return sources


def module_metadata() -> dict[str, dict[str, str]]:
    output = git(["config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.(path|url)$"])
    modules: dict[str, dict[str, str]] = {}
    for line in output.splitlines():
        key, value = line.split(None, 1)
        match = re.fullmatch(r"submodule\.(.+)\.(path|url)", key)
        if not match:
            continue
        name, field = match.groups()
        modules.setdefault(name, {})[field] = value.strip()
    return modules


def gitlink_entries() -> dict[str, tuple[str, str]]:
    output = git(["ls-files", "--stage", "-z"])
    entries: dict[str, tuple[str, str]] = {}
    for record in output.split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        mode, sha, _stage = metadata.split()
        if mode == "160000":
            entries[path.replace("\\", "/")] = (sha, mode)
    return entries


def meaningful_source_files(source: dict, checkout: Path) -> list[str]:
    name = source["name"]
    if source["source_kind"] == "app":
        app_dir = "india_payroll" if name == "india_payroll" else name
        required = [checkout / "pyproject.toml", checkout / app_dir]
    elif name == "frappe_docker":
        required = [checkout / "images", checkout / "pwd.yml"]
        if not required[1].exists():
            required[1] = checkout / "compose.yaml"
    else:
        required = [checkout / "erpnext" / "Chart.yaml", checkout / "erpnext" / "templates"]
    return [path.relative_to(checkout).as_posix() for path in required if path.exists()]


def nested_git_repositories(checkout: Path) -> list[str]:
    nested: list[str] = []
    for current, dirs, _files in os.walk(checkout):
        current_path = Path(current)
        if current_path == checkout:
            dirs[:] = [directory for directory in dirs if directory != ".git"]
            continue
        if ".git" in dirs or (current_path / ".git").is_file():
            nested.append((current_path / ".git").relative_to(checkout).as_posix())
            dirs[:] = []
    return nested


def verify_one(source: dict, modules: dict, gitlinks: dict) -> dict:
    rel = source["path"]
    checkout = ROOT / Path(rel)
    errors: list[str] = []
    result = {
        **source,
        "exists": checkout.is_dir(),
        "repository_valid": False,
        "remote": None,
        "remote_matches": False,
        "actual_sha": None,
        "expected_sha_matches": False,
        "gitlink_sha": None,
        "gitlink_matches": False,
        "submodule_registered": False,
        "submodule_initialized": False,
        "sparse_checkout": None,
        "working_tree_clean": False,
        "meaningful_source_files": [],
        "license_files": [],
        "nested_repositories": [],
        "errors": errors,
    }

    matching_modules = [
        (module_name, metadata)
        for module_name, metadata in modules.items()
        if metadata.get("path", "").replace("\\", "/") == rel
    ]
    if len(matching_modules) == 1:
        _module_name, metadata = matching_modules[0]
        result["submodule_registered"] = True
        result["submodule_url"] = metadata.get("url")
        result["module_url_matches"] = canonical_url(metadata.get("url", "")) == canonical_url(
            source["repository"]
        )
        if not result["module_url_matches"]:
            errors.append(".gitmodules URL does not match the lockfile canonical repository")
    else:
        result["module_url_matches"] = False
        errors.append("expected exactly one .gitmodules entry for this path")

    gitlink = gitlinks.get(rel)
    if gitlink:
        result["gitlink_sha"] = gitlink[0]
        result["gitlink_matches"] = gitlink[0] == source["commit"]
    if not result["gitlink_matches"]:
        errors.append("index does not contain the exact locked submodule gitlink")

    if not checkout.is_dir():
        errors.append("submodule directory is missing or uninitialized")
        return result

    inside = git(["rev-parse", "--is-inside-work-tree"], cwd=checkout, check=False)
    result["repository_valid"] = inside == "true"
    if not result["repository_valid"]:
        errors.append("directory is not an initialized Git working tree")
        return result

    result["submodule_initialized"] = True
    result["actual_sha"] = git(["rev-parse", "HEAD"], cwd=checkout)
    result["expected_sha_matches"] = result["actual_sha"] == source["commit"]
    if not result["expected_sha_matches"]:
        errors.append("checked-out HEAD does not match the locked commit")

    result["remote"] = git(["remote", "get-url", "origin"], cwd=checkout, check=False) or None
    result["remote_matches"] = bool(result["remote"]) and canonical_url(
        result["remote"] or ""
    ) == canonical_url(source["repository"])
    if not result["remote_matches"]:
        errors.append("origin remote does not match the canonical lockfile repository")

    sparse = git(["config", "--bool", "core.sparseCheckout"], cwd=checkout, check=False)
    result["sparse_checkout"] = sparse == "true"
    if result["sparse_checkout"]:
        errors.append("sparse checkout is enabled")

    status = git(["status", "--porcelain", "--untracked-files=all"], cwd=checkout, check=False)
    result["working_tree_clean"] = not status
    if status:
        errors.append(f"source working tree has unrelated changes: {status.splitlines()[:5]}")

    result["meaningful_source_files"] = meaningful_source_files(source, checkout)
    expected_source_count = 2
    if len(result["meaningful_source_files"]) != expected_source_count:
        errors.append("expected application/deployment source files are missing")

    result["license_files"] = sorted(
        path.name
        for path in checkout.iterdir()
        if path.is_file() and LICENSE_NAME.match(path.name)
    )
    if not result["license_files"]:
        errors.append("no root license/copyright evidence file is present")

    result["nested_repositories"] = nested_git_repositories(checkout)
    if result["nested_repositories"]:
        errors.append(f"unexpected nested Git repositories: {result['nested_repositories']}")
    return result


def verify(report_path: Path) -> dict:
    sources = load_sources()
    modules = module_metadata()
    gitlinks = gitlink_entries()
    expected_paths = {source["path"] for source in sources}
    actual_module_paths = {
        metadata.get("path", "").replace("\\", "/") for metadata in modules.values()
    }
    actual_gitlink_paths = set(gitlinks)
    errors: list[str] = []
    for description, actual in (
        (".gitmodules", actual_module_paths),
        ("Git index", actual_gitlink_paths),
    ):
        if actual != expected_paths:
            errors.append(
                f"{description} submodule paths differ from lock: "
                f"missing={sorted(expected_paths - actual)}, unexpected={sorted(actual - expected_paths)}"
            )
    rows = [verify_one(source, modules, gitlinks) for source in sources]
    for row in rows:
        errors.extend(f"{row['name']}: {message}" for message in row["errors"])
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository": str(ROOT),
        "result": "PASS" if not errors else "FAIL",
        "expected_sources": len(sources),
        "registered_submodules": len(modules),
        "initialized_sources": sum(row["submodule_initialized"] for row in rows),
        "errors": errors,
        "sources": rows,
        "report_path": str(report_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    try:
        report = verify(args.report)
    except Exception as exc:
        report = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "repository": str(ROOT),
            "result": "FAIL",
            "errors": [str(exc)],
            "sources": [],
            "report_path": str(args.report),
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for row in report.get("sources", []):
        state = "PASS" if not row["errors"] else "FAIL"
        print(f"{state} {row['name']}: {row['actual_sha']} ({row['path']})")
        for message in row["errors"]:
            print(f"  - {message}", file=sys.stderr)
    for message in report.get("errors", []):
        print(f"ERROR: {message}", file=sys.stderr)
    print(f"{report.get('result', 'FAIL')}: {report.get('initialized_sources', 0)}/{report.get('expected_sources', 10)} sources; report={args.report}")
    return 0 if report.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
