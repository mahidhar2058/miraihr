#!/usr/bin/env python3
"""Fetch and validate the immutable upstream revisions in the candidate lock."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version


LOCK = Path(os.environ.get("MIRAIHR_LOCK", "deployment/dependencies.lock.json"))
REPORT = Path(os.environ.get("MIRAIHR_REPORT_DIR", "artifacts"))
FRAPPE_VERSION = Version("16.53.0")
PYTHON_VERSION = Version("3.14.0")
NODE_VERSION = Version("24.0.0")
APP_ORDER = (
    "frappe",
    "erpnext",
    "hrms",
    "india_payroll",
    "telephony",
    "helpdesk",
    "payments",
    "lms",
)
LICENSE_FILES = (
    "LICENSE",
    "LICENSE.txt",
    "license.txt",
    "LICENCE",
    "LICENCE.txt",
    "license",
)


def run(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout.strip()


def check_runtime(project: dict, app_name: str) -> dict[str, str | None]:
    project_meta = project.get("project", {})
    requires_python = project_meta.get("requires-python")
    if requires_python and PYTHON_VERSION not in SpecifierSet(requires_python):
        raise ValueError(f"{app_name} requires-python {requires_python} excludes 3.14")

    bench_dependencies = (
        project.get("tool", {}).get("bench", {}).get("frappe-dependencies", {})
    )
    frappe_requirement = bench_dependencies.get("frappe")
    if app_name != "frappe" and frappe_requirement:
        if FRAPPE_VERSION not in SpecifierSet(frappe_requirement):
            raise ValueError(
                f"{app_name} requires Frappe {frappe_requirement}, "
                f"which excludes {FRAPPE_VERSION}"
            )

    node_requirement = None
    package_json = project.get("package-json")
    if package_json:
        node_requirement = package_json.get("engines", {}).get("node")
        if node_requirement:
            try:
                compatible = NODE_VERSION in SpecifierSet(node_requirement)
            except Exception:
                # npm engine expressions use semver syntax, which differs from PEP 440.
                compatible = bool(re.search(r"(?:>=|\^|\|\|\s*)\s*2[4-9]", node_requirement))
            if not compatible:
                raise ValueError(
                    f"{app_name} node engine {node_requirement} excludes Node 24"
                )

    return {
        "requires_python": requires_python,
        "requires_frappe": frappe_requirement,
        "requires_node": node_requirement,
    }


def main() -> int:
    REPORT.mkdir(parents=True, exist_ok=True)
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    if lock.get("lock_status") != "candidate_unvalidated":
        raise ValueError("Do not mark this candidate lock validated before runtime tests pass")

    applications = {app["name"]: app for app in lock["applications"]}
    records = []
    root = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "miraihr-upstream-validation"
    root.mkdir(parents=True, exist_ok=True)

    for app_name in APP_ORDER:
        app = applications[app_name]
        sha = app["commit"]
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError(f"{app_name} does not have a full immutable commit SHA")

        checkout = root / app_name
        if checkout.exists():
            raise ValueError(f"Refusing to overwrite existing validation checkout: {checkout}")
        checkout.mkdir()
        run(["git", "init", "--quiet", str(checkout)])
        run(["git", "remote", "add", "origin", app["repository"]], cwd=checkout)
        run(["git", "fetch", "--quiet", "--depth=1", "--filter=blob:none", "origin", sha], cwd=checkout)
        run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=checkout)
        actual_sha = run(["git", "rev-parse", "HEAD"], cwd=checkout)
        if actual_sha != sha:
            raise ValueError(f"{app_name}: expected {sha}, checked out {actual_sha}")

        pyproject_path = checkout / "pyproject.toml"
        if not pyproject_path.is_file():
            raise ValueError(f"{app_name}: pyproject.toml is missing at pinned commit")
        project = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        project_meta = project.get("project", {})
        package_json_path = checkout / "package.json"
        if package_json_path.is_file():
            project["package-json"] = json.loads(
                package_json_path.read_text(encoding="utf-8")
            )
        runtime = check_runtime(project, app_name)

        mariadb_ci_images: list[str] = []
        if app_name == "frappe":
            for workflow_path in (checkout / ".github/workflows").glob("**/*"):
                if workflow_path.is_file():
                    workflow_text = workflow_path.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    mariadb_ci_images.extend(
                        re.findall(r"mariadb:(11\.8(?:\.\d+)?)", workflow_text)
                    )
            if not mariadb_ci_images:
                raise ValueError(
                    "Pinned Frappe source has no MariaDB 11.8 CI image reference; "
                    "review the configured integration database version."
                )

        bench_dependencies = (
            project.get("tool", {}).get("bench", {}).get("frappe-dependencies", {})
        )
        for dependency, requirement in app.get("requires_apps", {}).items():
            actual_requirement = bench_dependencies.get(dependency)
            if actual_requirement != requirement:
                # The lock and upstream may express equivalent constraints with spacing.
                if not actual_requirement or SpecifierSet(actual_requirement) != SpecifierSet(requirement):
                    raise ValueError(
                        f"{app_name}: lock requires {dependency} {requirement}, "
                        f"upstream declares {actual_requirement!r}"
                    )

        license_file = next((name for name in LICENSE_FILES if (checkout / name).is_file()), None)
        if not license_file:
            raise ValueError(f"{app_name}: no recognized license file at pinned commit")

        record = {
            "name": app_name,
            "repository": app["repository"],
            "ref": app["ref"],
            "bootstrap_ref": app.get("bootstrap_ref", app["ref"]),
            "expected_commit": sha,
            "actual_commit": actual_sha,
            "project_name": project_meta.get("name"),
            "requires_python": runtime["requires_python"],
            "requires_frappe": runtime["requires_frappe"],
            "requires_node": runtime["requires_node"],
            "mariadb_ci_images": sorted(set(mariadb_ci_images)),
            "integration_database_image": (
                "mariadb:11.8.3" if app_name == "frappe" else None
            ),
            "integration_database_basis": (
                "Exact CI patch selected within the MariaDB 11.8 series used by "
                "the pinned Frappe source CI."
                if app_name == "frappe"
                else None
            ),
            "frappe_dependencies": bench_dependencies,
            "license_file": license_file,
            "license_sha256": run(
                ["sha256sum", license_file], cwd=checkout
            ).split()[0],
            "status": "source_sha_and_metadata_verified",
        }
        records.append(record)
        print(
            f"VERIFIED {app_name}: {actual_sha} "
            f"(Python {runtime['requires_python']}, Frappe {runtime['requires_frappe']})"
        )

    deployment_sources = lock.get("deployment_sources", {})
    for source_name in ("frappe_docker", "frappe_helm"):
        source = deployment_sources[source_name]
        sha = source["commit"]
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError(f"{source_name} does not have a full immutable commit SHA")
        checkout = root / source_name
        if checkout.exists():
            raise ValueError(f"Refusing to overwrite existing validation checkout: {checkout}")
        checkout.mkdir()
        run(["git", "init", "--quiet", str(checkout)])
        run(["git", "remote", "add", "origin", source["repository"]], cwd=checkout)
        run(["git", "fetch", "--quiet", "--depth=1", "--filter=blob:none", "origin", sha], cwd=checkout)
        run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=checkout)
        actual_sha = run(["git", "rev-parse", "HEAD"], cwd=checkout)
        if actual_sha != sha:
            raise ValueError(f"{source_name}: expected {sha}, checked out {actual_sha}")

        license_file = next((name for name in LICENSE_FILES if (checkout / name).is_file()), None)
        if not license_file:
            raise ValueError(f"{source_name}: no recognized license file at pinned commit")
        records.append(
            {
                "name": source_name,
                "repository": source["repository"],
                "ref": source.get("ref", source.get("chart_version")),
                "expected_commit": sha,
                "actual_commit": actual_sha,
                "license_file": license_file,
                "license_sha256": run(["sha256sum", license_file], cwd=checkout).split()[0],
                "status": "source_sha_and_license_file_verified",
            }
        )
        print(f"VERIFIED {source_name}: {actual_sha}")

    output = {
        "lock_status": lock["lock_status"],
        "integration_status": "not_tested_by_source_validation_job",
        "frappe_candidate": str(FRAPPE_VERSION),
        "python_candidate": str(PYTHON_VERSION),
        "node_candidate": str(NODE_VERSION),
        "applications": records,
    }
    (REPORT / "upstream-source-validation.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
