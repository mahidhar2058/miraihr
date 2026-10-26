#!/usr/bin/env python3
"""Validate pinned source metadata and always emit a diagnostic JSON report."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

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
DEPLOYMENT_SOURCES = ("frappe_docker", "frappe_helm")
KNOWN_APPS = {*APP_ORDER, "miraihr_core"}
LICENSE_BASENAMES = re.compile(
	r"^(?:licen[cs]e|copying|unlicense)(?:(?:\.(?:md|markdown|txt|rst|rtf|lesser|gpl|agpl|lgpl))|(?:-(?:mit|apache|bsd|gpl|agpl|lgpl)(?:\.(?:md|markdown|txt|rst|rtf))?))?$",
	re.IGNORECASE,
)
LICENSE_DIRS = {"license", "licenses", "legal"}


class ValidationError(ValueError):
	"""A source or metadata check failed and should be recorded in the report."""


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


def validate_source_metadata(name: str, source: dict) -> str:
	"""Validate the minimum source identity needed before fetching it."""
	if not isinstance(source, dict):
		raise ValidationError(f"{name}: source metadata must be an object")
	repository = source.get("repository")
	parsed = urlparse(repository or "")
	if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
		raise ValidationError(f"{name}: repository must be a canonical HTTPS GitHub URL")
	if parsed.query or parsed.fragment or not parsed.path.strip("/"):
		raise ValidationError(f"{name}: repository URL is not a plain repository URL")
	sha = source.get("commit")
	if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
		raise ValidationError(f"{name}: commit must be a full lowercase immutable SHA")
	return sha


def verify_revision(name: str, expected: str, actual: str) -> None:
	if actual != expected:
		raise ValidationError(f"{name}: expected pinned SHA {expected}, checked out {actual}")


def _license_candidates(repository: Path) -> list[Path]:
	candidates: list[Path] = []
	for child in repository.iterdir():
		if child.is_file() and LICENSE_BASENAMES.fullmatch(child.name):
			candidates.append(child)
		elif child.is_dir() and child.name.casefold() in LICENSE_DIRS:
			for nested in child.iterdir():
				if nested.is_file() and LICENSE_BASENAMES.fullmatch(nested.name):
					candidates.append(nested)
	return sorted(candidates, key=lambda path: path.as_posix().casefold())


def classify_license_text(text: str) -> str:
	"""Identify supported license families from their text, never the filename."""
	content = text.upper()
	if len(text.strip()) < 100:
		raise ValidationError("license file is empty or too short to contain license text")
	gpl_title = re.search(
		r"GNU\s+(?:(AFFERO|LESSER)\s+)?GENERAL PUBLIC LICENSE",
		content,
	)
	if gpl_title:
		# GPL-3's body itself mentions AGPL, so classify using the first license
		# title and its nearby version line rather than any later body text.
		family = gpl_title.group(1) or "GPL"
		header = content[gpl_title.start() : gpl_title.start() + 400]
		version = re.search(r"VERSION\s+(\d+(?:\.\d+)?)", header)
		version_number = version.group(1) if version else None
		if version_number in {"2", "3"}:
			version_number += ".0"
		if family == "AFFERO":
			return f"AGPL-{version_number}" if version_number else "AGPL-unknown-version"
		if family == "LESSER":
			return f"LGPL-{version_number}" if version_number else "LGPL-unknown-version"
		return f"GPL-{version_number}" if version_number else "GPL-unknown-version"
	if "MIT LICENSE" in content or (
		"PERMISSION IS HEREBY GRANTED, FREE OF CHARGE" in content
		and "THE SOFTWARE IS PROVIDED \"AS IS\"" in content
	):
		return "MIT"
	if "APACHE LICENSE" in content and re.search(r"VERSION\s+2\.0", content):
		return "Apache-2.0"
	if "MOZILLA PUBLIC LICENSE" in content and "VERSION 2.0" in content:
		return "MPL-2.0"
	if (
		"REDISTRIBUTION AND USE IN SOURCE AND BINARY FORMS" in content
		and "ARE PERMITTED PROVIDED THAT" in content
	):
		return "BSD"
	if "THIS IS FREE AND UNENCUMBERED SOFTWARE RELEASED INTO THE PUBLIC DOMAIN" in content:
		return "Unlicense"
	raise ValidationError("license file exists but its license text could not be classified")


def declared_license_family(value: object) -> str:
	if not isinstance(value, str) or not value.strip():
		raise ValidationError("lock metadata has no declared license to compare with source text")
	declared = value.upper()
	if "AGPL" in declared:
		return "AGPL"
	if "LGPL" in declared:
		return "LGPL"
	if "GPL" in declared:
		return "GPL"
	if "MIT" in declared:
		return "MIT"
	if "APACHE" in declared:
		return "APACHE"
	if "MPL" in declared:
		return "MPL"
	if "BSD" in declared:
		return "BSD"
	if "UNLICENSE" in declared:
		return "UNLICENSE"
	raise ValidationError(f"unsupported or ambiguous declared license value: {value!r}")


def inspect_license(repository: Path, declared_license: object) -> dict:
	candidates = _license_candidates(repository)
	if not candidates:
		raise ValidationError("no recognized license file in repository root or known license directories")
	if len(candidates) > 1:
		paths = [path.relative_to(repository).as_posix() for path in candidates]
		raise ValidationError(f"ambiguous license metadata; found multiple candidates: {paths}")
	path = candidates[0]
	text = path.read_text(encoding="utf-8", errors="replace")
	classification = classify_license_text(text)
	declared_family = declared_license_family(declared_license)
	actual_family = classification.split("-", 1)[0].upper()
	if actual_family != declared_family:
		raise ValidationError(
			f"license text identifies {classification}, but lock declares {declared_license!r}"
		)
	return {
		"file_found": True,
		"path": path.relative_to(repository).as_posix(),
		"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
		"classification": classification,
		"declared_license": declared_license,
		"content_verified": True,
		"obligations_reviewed": False,
		"commercial_redistribution_approved": False,
	}


def check_runtime(project: dict, app_name: str) -> dict[str, str | None]:
	project_meta = project.get("project", {})
	requires_python = project_meta.get("requires-python")
	if requires_python and PYTHON_VERSION not in SpecifierSet(requires_python):
		raise ValidationError(f"{app_name} requires-python {requires_python} excludes 3.14")

	bench_dependencies = (
		project.get("tool", {}).get("bench", {}).get("frappe-dependencies", {})
	)
	frappe_requirement = bench_dependencies.get("frappe")
	if app_name != "frappe" and frappe_requirement:
		if FRAPPE_VERSION not in SpecifierSet(frappe_requirement):
			raise ValidationError(
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
				# npm uses semver syntax rather than PEP 440.
				compatible = bool(re.search(r"(?:>=|\^|\|\|\s*)\s*2[4-9]", node_requirement))
			if not compatible:
				raise ValidationError(
					f"{app_name} node engine {node_requirement} excludes Node 24"
				)

	return {
		"requires_python": requires_python,
		"requires_frappe": frappe_requirement,
		"requires_node": node_requirement,
		"status": "pass",
	}


def checkout_source(name: str, source: dict, checkout: Path, runner: Path) -> str:
	sha = validate_source_metadata(name, source)
	if checkout.exists():
		raise ValidationError(f"refusing to overwrite existing validation checkout: {checkout}")
	checkout.mkdir(parents=True)
	run(["git", "init", "--quiet", str(checkout)])
	run(["git", "remote", "add", "origin", source["repository"]], cwd=checkout)
	run(["git", "fetch", "--quiet", "--depth=1", "--filter=blob:none", "origin", sha], cwd=checkout)
	run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=checkout)
	return run(["git", "rev-parse", "HEAD"], cwd=checkout)


def validate_source_entry(name: str, source: dict, checkout_root: Path) -> dict:
	sha = source.get("commit") if isinstance(source, dict) else None
	record = {
		"repository": source.get("repository") if isinstance(source, dict) else None,
		"expected_sha": sha,
		"actual_sha": None,
		"revision_verified": False,
		"dependency_compatibility": {"status": "not_checked"},
		"license": {
			"file_found": False,
			"candidate_paths": [],
			"path": None,
			"classification": None,
			"content_verified": False,
			"obligations_reviewed": False,
			"commercial_redistribution_approved": False,
		},
		"validation_errors": [],
	}
	if name not in KNOWN_APPS:
		record["dependency_compatibility"] = {"status": "not_applicable"}
	try:
		sha = validate_source_metadata(name, source)
		record["expected_sha"] = sha
		repository = urlparse(source["repository"]).path.rstrip("/").split("/")[-1].removesuffix(".git")
		checkout = checkout_root / f"{name}-{repository}"
		actual_sha = checkout_source(name, source, checkout, checkout_root)
		record["actual_sha"] = actual_sha
		verify_revision(name, sha, actual_sha)
		record["revision_verified"] = True
	except Exception as exc:
		record["validation_errors"].append(str(exc))
		return record
	if name in KNOWN_APPS and name != "miraihr_core":
		try:
			pyproject_path = checkout / "pyproject.toml"
			if not pyproject_path.is_file():
				raise ValidationError(f"{name}: pyproject.toml is missing at pinned commit")
			project = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
			project_meta = project.get("project", {})
			package_json_path = checkout / "package.json"
			if package_json_path.is_file():
				project["package-json"] = json.loads(package_json_path.read_text(encoding="utf-8"))
			runtime = check_runtime(project, name)
			bench_dependencies = project.get("tool", {}).get("bench", {}).get("frappe-dependencies", {})
			for dependency, requirement in source.get("requires_apps", {}).items():
				if dependency not in KNOWN_APPS or dependency == "miraihr_core":
					raise ValidationError(f"{name}: unknown dependency {dependency!r} in lock metadata")
				actual_requirement = bench_dependencies.get(dependency)
				if actual_requirement != requirement:
					if not actual_requirement or SpecifierSet(actual_requirement) != SpecifierSet(requirement):
						raise ValidationError(
							f"{name}: lock requires {dependency} {requirement}, "
							f"upstream declares {actual_requirement!r}"
						)
			record["project_name"] = project_meta.get("name")
			record["dependency_compatibility"] = {
				**runtime,
				"declared_app_dependencies": bench_dependencies,
			}
			if name == "frappe":
				mariadb_ci_images = []
				for workflow_path in (checkout / ".github/workflows").glob("**/*"):
					if workflow_path.is_file():
						workflow_text = workflow_path.read_text(encoding="utf-8", errors="replace")
						mariadb_ci_images.extend(re.findall(r"mariadb:(11\.8(?:\.\d+)?)", workflow_text))
				if not mariadb_ci_images:
					raise ValidationError("pinned Frappe source CI has no MariaDB 11.8 reference")
				record["dependency_compatibility"]["mariadb_ci_images"] = sorted(set(mariadb_ci_images))
			record["dependency_compatibility"]["status"] = "pass"
		except Exception as exc:
			record["dependency_compatibility"]["status"] = "fail"
			record["validation_errors"].append(str(exc))
	try:
		candidates = _license_candidates(checkout)
		record["license"]["candidate_paths"] = [
			path.relative_to(checkout).as_posix() for path in candidates
		]
		record["license"]["file_found"] = bool(candidates)
		if len(candidates) == 1:
			record["license"]["path"] = candidates[0].relative_to(checkout).as_posix()
		record["license"].update(inspect_license(checkout, source.get("license")))
	except Exception as exc:
		record["validation_errors"].append(str(exc))
	return record


def _locked_source_entries(lock: dict) -> tuple[list[tuple[str, dict]], list[dict]]:
	errors: list[dict] = []
	applications = lock.get("applications")
	if not isinstance(applications, list):
		raise ValidationError("lock applications must be a list")
	by_name: dict[str, dict] = {}
	for entry in applications:
		if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
			errors.append({"source": "lock", "message": "application entry has invalid metadata"})
			continue
		name = entry["name"]
		if name in by_name:
			errors.append({"source": name, "message": "duplicate application entry"})
		by_name[name] = entry
	unknown = sorted(set(by_name) - KNOWN_APPS)
	for name in unknown:
		errors.append({"source": name, "message": "unknown application/dependency in lock; add explicit validation support"})
	for name in APP_ORDER:
		if name not in by_name:
			errors.append({"source": name, "message": "required application is missing from lock"})
	if "miraihr_core" not in by_name:
		errors.append({"source": "miraihr_core", "message": "local Core license status is missing from lock"})

	entries = [(name, by_name[name]) for name in APP_ORDER if name in by_name]
	deployment = lock.get("deployment_sources")
	if not isinstance(deployment, dict):
		errors.append({"source": "deployment_sources", "message": "deployment_sources must be an object"})
		deployment = {}
	for name in DEPLOYMENT_SOURCES:
		if name not in deployment:
			errors.append({"source": name, "message": "required deployment source is missing from lock"})
		else:
			entries.append((name, deployment[name]))
	for name in sorted(set(deployment) - set(DEPLOYMENT_SOURCES) - {"frappe_erpnext_image_candidate"}):
		errors.append({"source": name, "message": "unknown deployment source in lock; add explicit validation support"})
	return entries, errors


def _core_license_record(lock: dict) -> dict:
	core = next((entry for entry in lock.get("applications", []) if entry.get("name") == "miraihr_core"), {})
	return {
		"repository": "local",
		"expected_sha": core.get("commit"),
		"actual_sha": None,
		"revision_verified": False,
		"dependency_compatibility": {"status": "local_app_not_validated_by_source_job"},
		"license": {
			"file_found": False,
			"path": None,
			"classification": "UNRESOLVED",
			"content_verified": False,
			"obligations_reviewed": False,
			"commercial_redistribution_approved": False,
			"status": "owner_legal_decision_required",
		},
		"validation_errors": [],
	}


def write_report(path: Path, report: dict) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_validation(
	lock_path: Path = LOCK,
	report_path: Path | None = None,
	checkout_root: Path | None = None,
	validator=validate_source_entry,
) -> dict:
	report_path = report_path or REPORT / "upstream-source-validation.json"
	checkout_root = checkout_root or Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "miraihr-upstream-validation"
	report = {
		"timestamp_utc": datetime.now(timezone.utc).isoformat(),
		"overall_result": "FAIL",
		"lock_status": None,
		"integration_status": "not_tested_by_source_validation_job",
		"frappe_candidate": str(FRAPPE_VERSION),
		"python_candidate": str(PYTHON_VERSION),
		"node_candidate": str(NODE_VERSION),
		"repositories": {},
		"validation_errors": [],
	}
	try:
		lock = json.loads(lock_path.read_text(encoding="utf-8"))
		if not isinstance(lock, dict):
			raise ValidationError("dependency lock root must be a JSON object")
		report["lock_status"] = lock.get("lock_status")
		if lock.get("lock_status") != "candidate_unvalidated":
			report["validation_errors"].append({"source": "lock", "message": "refusing a lock status other than candidate_unvalidated"})
		entries, metadata_errors = _locked_source_entries(lock)
		report["validation_errors"].extend(metadata_errors)
		for name, source in entries:
			row = {
				"repository": source.get("repository") if isinstance(source, dict) else None,
				"expected_sha": source.get("commit") if isinstance(source, dict) else None,
				"actual_sha": None,
				"revision_verified": False,
				"dependency_compatibility": {"status": "not_checked"},
				"license": {
					"file_found": False,
					"path": None,
					"classification": None,
					"content_verified": False,
					"obligations_reviewed": False,
					"commercial_redistribution_approved": False,
				},
				"validation_errors": [],
			}
			report["repositories"][name] = row
			try:
				validated = validator(name, source, checkout_root)
				row.update(validated)
				for message in row["validation_errors"]:
					report["validation_errors"].append({"source": name, "message": message})
			except Exception as exc:  # Record every repository failure and continue diagnostics.
				row["validation_errors"].append(str(exc))
				report["validation_errors"].append({"source": name, "message": str(exc)})
		core_row = _core_license_record(lock)
		report["repositories"]["miraihr_core"] = core_row
		core = next((entry for entry in lock.get("applications", []) if entry.get("name") == "miraihr_core"), None)
		if core is None:
			report["validation_errors"].append({"source": "miraihr_core", "message": "local Core licensing status is missing"})
	except Exception as exc:
		report["validation_errors"].append({"source": "lock", "message": str(exc)})
	finally:
		report["overall_result"] = "PASS" if not report["validation_errors"] else "FAIL"
		write_report(report_path, report)
	return report


def main() -> int:
	report_path = REPORT / "upstream-source-validation.json"
	try:
		report = run_validation(LOCK, report_path)
	except Exception as exc:
		print(f"ERROR: failed to write source validation report {report_path}: {exc}", file=sys.stderr)
		return 1
	for name, row in report["repositories"].items():
		if row["validation_errors"]:
			print(f"FAIL {name}: {'; '.join(row['validation_errors'])}", file=sys.stderr)
		elif row["license"]["classification"] == "UNRESOLVED":
			print(f"REVIEW {name}: license remains unresolved by owner/legal decision")
		else:
			print(f"VERIFIED {name}: {row['actual_sha']} ({row['license']['classification']})")
	if report["validation_errors"]:
		for error in report["validation_errors"]:
			print(f"ERROR {error['source']}: {error['message']}", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
