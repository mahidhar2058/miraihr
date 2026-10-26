import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.evaluate_trivy_report import summarize


EXPECTED_DIGEST = "sha256:" + "a" * 64


class TrivyReportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.json_path = self.root / "trivy.json"
        self.sarif_path = self.root / "trivy.sarif"
        self.write_reports([])

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_reports(self, vulnerabilities, digest=EXPECTED_DIGEST):
        self.json_path.write_text(
            json.dumps(
                {
                    "Metadata": {"RepoDigests": [f"docker.io/frappe/erpnext@{digest}"]},
                    "Results": [
                        {
                            "Target": "frappe/erpnext",
                            "Vulnerabilities": vulnerabilities,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.sarif_path.write_text(
            json.dumps({"version": "2.1.0", "runs": [{"results": []}]}),
            encoding="utf-8",
        )

    def verify(self, *, json_outcome="success", sarif_outcome="success", gitleaks_outcome="success"):
        return summarize(
            self.json_path,
            self.sarif_path,
            EXPECTED_DIGEST,
            f"frappe/erpnext:v16@{EXPECTED_DIGEST}",
            json_outcome,
            sarif_outcome,
            gitleaks_outcome,
        )

    def test_clean_scan_passes_and_records_zero_counts(self):
        result = self.verify()
        self.assertEqual(result["result"], "PASS")
        self.assertTrue(result["scan_reference_digest_verified"])
        self.assertEqual(result["severity_counts"]["HIGH"], 0)
        self.assertEqual(result["severity_counts"]["CRITICAL"], 0)

    def test_high_and_critical_findings_fail_with_fix_evidence(self):
        self.write_reports(
            [
                {
                    "VulnerabilityID": "CVE-2099-1001",
                    "PkgName": "example-high",
                    "InstalledVersion": "1.0",
                    "FixedVersion": "1.2",
                    "Severity": "HIGH",
                },
                {
                    "VulnerabilityID": "CVE-2099-1002",
                    "PkgName": "example-critical",
                    "InstalledVersion": "2.0",
                    "FixedVersion": "",
                    "Severity": "CRITICAL",
                },
            ]
        )
        result = self.verify()
        self.assertEqual(result["result"], "FAIL")
        self.assertEqual(result["high_critical_gate_count"], 2)
        self.assertTrue(result["findings"][0]["fixed_version_available"])
        self.assertFalse(result["findings"][1]["fixed_version_available"])

    def test_wrong_image_digest_fails(self):
        self.write_reports([], digest="sha256:" + "b" * 64)
        result = self.verify()
        self.assertEqual(result["result"], "FAIL")
        self.assertFalse(result["scan_reference_digest_verified"])

    def test_scan_or_secret_job_failure_fails_gate(self):
        for result in (
            self.verify(json_outcome="failure"),
            self.verify(sarif_outcome="failure"),
            self.verify(gitleaks_outcome="failure"),
        ):
            self.assertEqual(result["result"], "FAIL")

    def test_missing_sarif_fails(self):
        self.sarif_path.unlink()
        result = self.verify()
        self.assertEqual(result["result"], "FAIL")
        self.assertTrue(any("SARIF evidence" in message for message in result["errors"]))

    def test_malformed_json_still_produces_a_failure_summary(self):
        self.json_path.write_text("not json", encoding="utf-8")
        result = self.verify()
        self.assertEqual(result["result"], "FAIL")
        self.assertTrue(any("JSON evidence" in message for message in result["errors"]))


if __name__ == "__main__":
    unittest.main()
