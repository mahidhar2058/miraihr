"""Authenticated, data-minimal landing page API."""

import frappe

from miraihr_core.navigation import build_navigation


@frappe.whitelist()
def get_navigation() -> list[dict[str, str]]:
    """Return role-filtered links only; no customer or employee records are queried."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)

    return build_navigation(frappe.get_roles(frappe.session.user), frappe.get_installed_apps())
