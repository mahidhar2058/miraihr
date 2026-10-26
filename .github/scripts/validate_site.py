#!/usr/bin/env python3
"""Apply and verify native Frappe branding and installed-app smoke checks."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import frappe


EXPECTED_APPS = {
    "frappe",
    "erpnext",
    "hrms",
    "india_payroll",
    "telephony",
    "helpdesk",
    "payments",
    "lms",
    "miraihr_core",
}
EXPECTED_WORKSPACES = {
    "Payroll": "HRMS",
    "Projects": "ERPNext",
    "India Payroll": "India Payroll",
    "Learning": "LMS",
    "Helpdesk": "Helpdesk",
}
LOGO_URL = "/assets/miraihr_core/images/miraihr-mark.svg"
FAVICON_URL = LOGO_URL


def main() -> None:
    bench_path = Path(os.environ["BENCH_PATH"]).resolve()
    site_name = os.environ["SITE_NAME"]
    frappe.init(site=site_name, sites_path=str(bench_path / "sites"))
    frappe.connect()
    try:
        installed_apps = set(frappe.get_installed_apps())
        missing_apps = sorted(EXPECTED_APPS - installed_apps)
        if missing_apps:
            raise AssertionError(f"Missing installed applications: {missing_apps}")

        required_doctypes = {
            "Employee",
            "Leave Application",
            "Salary Slip",
            "Project",
            "Task",
            "HD Ticket",
            "LMS Course",
        }
        missing_doctypes = sorted(
            doctype
            for doctype in required_doctypes
            if not frappe.db.exists("DocType", doctype)
        )
        if missing_doctypes:
            raise AssertionError(f"Missing expected upstream DocTypes: {missing_doctypes}")

        workspace_titles = set(
            frappe.get_all("Workspace", pluck="title")
        )
        missing_workspaces = sorted(set(EXPECTED_WORKSPACES) - workspace_titles)
        if missing_workspaces:
            raise AssertionError(
                f"Missing native upstream workspaces: {missing_workspaces}"
            )

        theme = frappe.get_doc(
            {
                "doctype": "Website Theme",
                "theme": "MiraiHR CI",
                "custom": 1,
                "custom_overrides": (
                    "$primary: #168b83;\n"
                    "$dark: #123b52;\n"
                    "$body-text-color: #123b52;\n"
                    "$body-bg: #ffffff;"
                ),
            }
        )
        theme.insert(ignore_permissions=True)
        frappe.db.set_single_value("Website Settings", "app_name", "MiraiHR")
        frappe.db.set_single_value("Website Settings", "app_logo", LOGO_URL)
        frappe.db.set_single_value("Website Settings", "favicon", FAVICON_URL)
        frappe.db.set_single_value("Website Settings", "website_theme", theme.name)
        frappe.db.set_single_value("Navbar Settings", "app_logo", LOGO_URL)
        frappe.db.commit()

        branding = {
            "website_app_name": frappe.db.get_single_value("Website Settings", "app_name"),
            "website_app_logo": frappe.db.get_single_value("Website Settings", "app_logo"),
            "website_favicon": frappe.db.get_single_value("Website Settings", "favicon"),
            "website_theme": frappe.db.get_single_value("Website Settings", "website_theme"),
            "navbar_app_logo": frappe.db.get_single_value("Navbar Settings", "app_logo"),
            "theme_url": frappe.db.get_value("Website Theme", theme.name, "theme_url"),
        }
        if branding["website_app_name"] != "MiraiHR":
            raise AssertionError(f"Website app name was not persisted: {branding}")
        for field in ("website_app_logo", "website_favicon", "navbar_app_logo"):
            if branding[field] != LOGO_URL:
                raise AssertionError(f"Expected {LOGO_URL} for {field}; got {branding[field]!r}")
        if branding["website_theme"] != "MiraiHR CI":
            raise AssertionError(f"Website theme was not saved: {branding['website_theme']!r}")
        if not branding["theme_url"]:
            raise AssertionError("Website Theme did not generate a CSS asset")
        output = {
            "status": "pass",
            "installed_apps": sorted(installed_apps),
            "verified_doctypes": sorted(required_doctypes),
            "verified_workspaces": EXPECTED_WORKSPACES,
            "workspace_permission_note": (
                "Workspace presence confirms navigation availability only; it does not "
                "verify role authorization or DocType permissions."
            ),
            "native_branding": branding,
            "theme": "MiraiHR CI",
            "favicon_format_note": (
                "SVG was accepted by Website Settings in this site test; Frappe's field "
                "description specifies .ico, so browser compatibility remains an assumption."
            ),
        }
        artifact_dir = Path(os.environ.get("ARTIFACT_DIR", "artifacts"))
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "site-branding-smoke.json").write_text(
            json.dumps(output, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(output, indent=2))
    finally:
        frappe.destroy()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
