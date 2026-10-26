from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_sources as validator  # noqa: E402


MIT_TEXT = """MIT License

Copyright (c) Example

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND.
"""

GPL_TEXT = """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

This is the full license grant and conditions text for the GNU GPL.
""" + ("The license terms and conditions apply. " * 12) + "Section 13 discusses the GNU Affero General Public License."


class LicenseDiscoveryTests(unittest.TestCase):
	def setUp(self) -> None:
		self.temp = tempfile.TemporaryDirectory()
		self.root = Path(self.temp.name)

	def tearDown(self) -> None:
		self.temp.cleanup()

	def test_common_root_license_filenames(self) -> None:
		for filename in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENSE.rst", "COPYING"):
			with self.subTest(filename=filename):
				for existing in self.root.iterdir():
					if existing.is_file():
						existing.unlink()
				(self.root / filename).write_text(MIT_TEXT, encoding="utf-8")
				evidence = validator.inspect_license(self.root, "MIT")
				self.assertEqual(evidence["path"], filename)
				self.assertEqual(evidence["classification"], "MIT")
				self.assertTrue(evidence["content_verified"])
				(self.root / filename).unlink()

	def test_case_insensitive_name_and_known_license_directory(self) -> None:
		license_dir = self.root / "LiCeNsEs"
		license_dir.mkdir()
		path = license_dir / "COPYING.MD"
		path.write_text(GPL_TEXT, encoding="utf-8")
		evidence = validator.inspect_license(self.root, "GPL-3.0")
		self.assertEqual(evidence["path"], "LiCeNsEs/COPYING.MD")
		self.assertEqual(evidence["classification"], "GPL-3.0")

	def test_missing_license_fails(self) -> None:
		with self.assertRaisesRegex(validator.ValidationError, "no recognized license"):
			validator.inspect_license(self.root, "MIT")

	def test_empty_license_fails(self) -> None:
		(self.root / "LICENSE.md").write_text("", encoding="utf-8")
		with self.assertRaisesRegex(validator.ValidationError, "empty or too short"):
			validator.inspect_license(self.root, "MIT")

	def test_ambiguous_license_files_fail(self) -> None:
		(self.root / "LICENSE").write_text(MIT_TEXT, encoding="utf-8")
		(self.root / "LICENSE.md").write_text(MIT_TEXT, encoding="utf-8")
		with self.assertRaisesRegex(validator.ValidationError, "ambiguous license metadata"):
			validator.inspect_license(self.root, "MIT")

	def test_filename_does_not_assign_license(self) -> None:
		(self.root / "LICENSE").write_text("A project readme, not a license." * 10, encoding="utf-8")
		with self.assertRaisesRegex(validator.ValidationError, "could not be classified"):
			validator.inspect_license(self.root, "MIT")

	def test_license_text_must_match_lock_declaration(self) -> None:
		(self.root / "LICENSE").write_text(MIT_TEXT, encoding="utf-8")
		with self.assertRaisesRegex(validator.ValidationError, "lock declares"):
			validator.inspect_license(self.root, "GPL-3.0")

	def test_gpl_body_reference_to_agpl_does_not_change_license_classification(self) -> None:
		self.assertEqual(validator.classify_license_text(GPL_TEXT), "GPL-3.0")

	def test_agpl_title_is_classified_separately_from_gpl(self) -> None:
		agpl = "GNU AFFERO GENERAL PUBLIC LICENSE\nVersion 3, 19 November 2007\n" + ("License conditions. " * 20)
		self.assertEqual(validator.classify_license_text(agpl), "AGPL-3.0")


class SourceMetadataTests(unittest.TestCase):
	def test_source_entry_records_pinned_helm_license_md_evidence(self) -> None:
		sha = "a" * 40
		source = {
			"repository": "https://github.com/frappe/helm",
			"commit": sha,
			"license": "MIT",
		}
		with tempfile.TemporaryDirectory() as temp_dir:
			root = Path(temp_dir)

			def fake_checkout(name: str, metadata: dict, checkout: Path, runner: Path) -> str:
				checkout.mkdir(parents=True)
				(checkout / "LICENSE.md").write_text(MIT_TEXT, encoding="utf-8")
				return metadata["commit"]

			with patch.object(validator, "checkout_source", side_effect=fake_checkout):
				record = validator.validate_source_entry("frappe_helm", source, root)
		self.assertEqual(record["validation_errors"], [])
		self.assertTrue(record["revision_verified"])
		self.assertEqual(record["expected_sha"], sha)
		self.assertEqual(record["actual_sha"], sha)
		self.assertEqual(record["license"]["path"], "LICENSE.md")
		self.assertEqual(record["license"]["classification"], "MIT")
		self.assertFalse(record["license"]["obligations_reviewed"])
		self.assertFalse(record["license"]["commercial_redistribution_approved"])

	def test_wrong_pinned_revision_fails(self) -> None:
		expected = "a" * 40
		with self.assertRaisesRegex(validator.ValidationError, "expected pinned SHA"):
			validator.verify_revision("helm", expected, "b" * 40)

	def test_invalid_repository_metadata_fails(self) -> None:
		with self.assertRaisesRegex(validator.ValidationError, "canonical HTTPS GitHub URL"):
			validator.validate_source_metadata(
				"frappe_helm",
				{"repository": "http://example.com/helm", "commit": "a" * 40},
			)

	def test_invalid_sha_metadata_fails(self) -> None:
		with self.assertRaisesRegex(validator.ValidationError, "full lowercase immutable SHA"):
			validator.validate_source_metadata(
				"frappe_helm",
				{"repository": "https://github.com/frappe/helm", "commit": "deadbeef"},
			)

	def test_partial_source_failure_still_writes_failure_report(self) -> None:
		applications = [
			{"name": name, "repository": f"https://github.com/frappe/{name}", "commit": "a" * 40, "license": "MIT"}
			for name in validator.APP_ORDER
		]
		applications.append({"name": "miraihr_core", "repository": "local", "commit": "b" * 40, "license": "UNLICENSED"})
		lock = {
			"lock_status": "candidate_unvalidated",
			"applications": applications,
			"deployment_sources": {
				name: {"repository": f"https://github.com/frappe/{name}", "commit": "c" * 40, "license": "MIT"}
				for name in validator.DEPLOYMENT_SOURCES
			},
		}
		with tempfile.TemporaryDirectory() as temp_dir:
			root = Path(temp_dir)
			lock_path = root / "lock.json"
			report_path = root / "artifacts" / "upstream-source-validation.json"
			lock_path.write_text(json.dumps(lock), encoding="utf-8")

			def fake_validator(name: str, source: dict, checkout_root: Path) -> dict:
				if name == "frappe_helm":
					raise validator.ValidationError("synthetic missing license")
				return {
					"repository": source["repository"],
					"expected_sha": source["commit"],
					"actual_sha": source["commit"],
					"revision_verified": True,
					"dependency_compatibility": {"status": "pass"},
					"license": {"file_found": True, "path": "LICENSE", "classification": "MIT"},
					"validation_errors": [],
				}

			report = validator.run_validation(lock_path, report_path, root / "checkouts", fake_validator)
			self.assertTrue(report_path.is_file())
			written = json.loads(report_path.read_text(encoding="utf-8"))
			self.assertEqual(report["overall_result"], "FAIL")
			self.assertEqual(written["repositories"]["frappe_helm"]["validation_errors"], ["synthetic missing license"])
			self.assertEqual(written["repositories"]["frappe"]["revision_verified"], True)

	def test_invalid_lock_still_writes_diagnostic_report(self) -> None:
		with tempfile.TemporaryDirectory() as temp_dir:
			root = Path(temp_dir)
			lock_path = root / "bad-lock.json"
			report_path = root / "artifacts" / "upstream-source-validation.json"
			lock_path.write_text("not json", encoding="utf-8")
			report = validator.run_validation(lock_path, report_path, root / "checkouts")
			self.assertEqual(report["overall_result"], "FAIL")
			self.assertTrue(report_path.is_file())
			self.assertIn("lock", report["validation_errors"][0]["source"])


if __name__ == "__main__":
	unittest.main()
