#!/usr/bin/env python3
"""Summarize pinned-image Trivy evidence and enforce its vulnerability gate."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SEVERITIES = ("UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL")
GATED_SEVERITIES = {"HIGH", "CRITICAL"}


def expected_digest_is_valid(value: str) -> bool:
    return re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def summarize(
    json_path: Path,
    sarif_path: Path,
    expected_digest: str,
    scan_reference: str,
    json_outcome: str,
    sarif_outcome: str,
    gitleaks_outcome: str,
) -> dict:
    errors: list[str] = []
    counts = {severity: 0 for severity in SEVERITIES}
    findings: list[dict] = []
    metadata: dict = {}
    sarif_result_count: int | None = None
    scan_reference_verified = False

    if not expected_digest_is_valid(expected_digest):
        errors.append("locked platform image digest is missing or malformed")
    scan_reference_pinned = scan_reference.endswith("@" + expected_digest)
    if not scan_reference_pinned:
        errors.append("Trivy input reference does not end in the locked platform image digest")
    if json_outcome != "success":
        errors.append(f"Trivy JSON scan step outcome was {json_outcome!r}")
    if sarif_outcome != "success":
        errors.append(f"Trivy SARIF scan step outcome was {sarif_outcome!r}")
    if gitleaks_outcome != "success":
        errors.append(f"Gitleaks scan step outcome was {gitleaks_outcome!r}")

    try:
        report = json.loads(json_path.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError("Trivy JSON root must be an object")
        metadata = report.get("Metadata") or {}
        if not isinstance(metadata, dict):
            raise ValueError("Trivy JSON Metadata must be an object")
        repo_digests = metadata.get("RepoDigests") or []
        if not isinstance(repo_digests, list):
            raise ValueError("Trivy JSON Metadata.RepoDigests must be an array")
        if any(str(value).endswith("@" + expected_digest) for value in repo_digests):
            scan_reference_verified = True
        else:
            errors.append(
                "Trivy JSON RepoDigests does not confirm the locked platform image digest"
            )

        results = report.get("Results") or []
        if not isinstance(results, list):
            raise ValueError("Trivy JSON Results must be an array")
        for result in results:
            if not isinstance(result, dict):
                continue
            vulnerabilities = result.get("Vulnerabilities") or []
            if not isinstance(vulnerabilities, list):
                errors.append("Trivy result Vulnerabilities must be an array")
                continue
            for vulnerability in vulnerabilities:
                if not isinstance(vulnerability, dict):
                    continue
                severity = str(vulnerability.get("Severity", "UNKNOWN")).upper()
                if severity not in counts:
                    severity = "UNKNOWN"
                counts[severity] += 1
                fixed_version = vulnerability.get("FixedVersion") or ""
                findings.append(
                    {
                        "target": result.get("Target"),
                        "vulnerability_id": vulnerability.get("VulnerabilityID"),
                        "package": vulnerability.get("PkgName"),
                        "installed_version": vulnerability.get("InstalledVersion"),
                        "fixed_version": fixed_version,
                        "fixed_version_available": bool(str(fixed_version).strip()),
                        "severity": severity,
                        "title": vulnerability.get("Title"),
                    }
                )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"Trivy JSON evidence is missing or invalid: {exc}")

    try:
        sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
        if not isinstance(sarif, dict) or not isinstance(sarif.get("runs"), list):
            raise ValueError("SARIF document must contain a runs array")
        sarif_result_count = 0
        for run in sarif["runs"]:
            if not isinstance(run, dict) or not isinstance(run.get("results", []), list):
                raise ValueError("SARIF run results must be an array")
            sarif_result_count += len(run.get("results", []))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"Trivy SARIF evidence is missing or invalid: {exc}")

    gated_count = sum(counts[severity] for severity in GATED_SEVERITIES)
    if gated_count:
        errors.append(f"HIGH/CRITICAL vulnerability policy failed with {gated_count} finding(s)")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "PASS" if not errors else "FAIL",
        "scan_scope": "pinned upstream frappe/erpnext base image only",
        "expected_platform_digest": expected_digest,
        "scan_reference": scan_reference,
        "scan_reference_pinned": scan_reference_pinned,
        "reported_image_id": metadata.get("ImageID"),
        "reported_repo_digests": metadata.get("RepoDigests", []),
        "scan_reference_digest_verified": scan_reference_verified,
        "scan_step_outcomes": {
            "json": json_outcome,
            "sarif": sarif_outcome,
            "gitleaks": gitleaks_outcome,
        },
        "severity_counts": counts,
        "high_critical_gate_count": gated_count,
        "sarif_result_count": sarif_result_count,
        "findings": findings,
        "errors": errors,
        "final_miraihr_image_built_or_scanned": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", dest="json_path", type=Path, required=True)
    parser.add_argument("--sarif", dest="sarif_path", type=Path, required=True)
    parser.add_argument("--expected-digest", required=True)
    parser.add_argument("--scan-reference", required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--json-outcome", default="unknown")
    parser.add_argument("--sarif-outcome", default="unknown")
    parser.add_argument("--gitleaks-outcome", default="unknown")
    args = parser.parse_args()
    try:
        summary = summarize(
            args.json_path,
            args.sarif_path,
            args.expected_digest,
            args.scan_reference,
            args.json_outcome,
            args.sarif_outcome,
            args.gitleaks_outcome,
        )
    except Exception as exc:
        summary = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "result": "FAIL",
            "scan_scope": "pinned upstream frappe/erpnext base image only",
            "expected_platform_digest": args.expected_digest,
            "scan_reference": args.scan_reference,
            "severity_counts": {severity: 0 for severity in SEVERITIES},
            "high_critical_gate_count": 0,
            "findings": [],
            "errors": [f"Unexpected report-evaluation error: {exc}"],
            "final_miraihr_image_built_or_scanned": False,
        }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for severity, count in summary["severity_counts"].items():
        print(f"{severity}: {count}")
    for finding in summary["findings"]:
        fixed = finding["fixed_version"] or "unavailable"
        print(
            f"{finding['severity']} {finding['vulnerability_id']} {finding['package']} "
            f"{finding['installed_version']} fixed={fixed}"
        )
    for error in summary["errors"]:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"{summary['result']}: Trivy summary written to {args.summary}")
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
