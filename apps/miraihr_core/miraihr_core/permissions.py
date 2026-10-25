"""Permission checks for MiraiHR Core entry points."""

from .navigation import build_navigation


def has_core_access() -> bool:
    """Expose the MiraiHR app tile only to users with at least one supported workflow."""
    import frappe

    roles = frappe.get_roles(frappe.session.user)
    installed_apps = frappe.get_installed_apps()
    return bool(build_navigation(roles, installed_apps))
