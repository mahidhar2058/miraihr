"""Pure role/app based navigation rules for the MiraiHR Desk landing page."""

from collections.abc import Iterable

_EMPLOYEE_ROLES = {"Employee", "Employee Self Service"}
_HR_ROLES = {"HR Manager", "HR User", "System Manager"}
_MANAGER_ROLES = {
    "HR Manager",
    "HR User",
    "System Manager",
    "Leave Approver",
    "Expense Approver",
    "Projects Manager",
}


def build_navigation(roles: Iterable[str], installed_apps: Iterable[str]) -> list[dict[str, str]]:
    """Return safe navigation entries; downstream routes enforce their own permissions."""
    role_set = set(roles)
    app_set = set(installed_apps)
    cards: list[dict[str, str]] = []

    if role_set & (_EMPLOYEE_ROLES | _HR_ROLES | _MANAGER_ROLES):
        cards.extend(
            [
                {"label": "My Leave", "route": "/app/leave-application"},
                {"label": "Attendance", "route": "/app/employee-checkin"},
                {"label": "My Payslips", "route": "/app/salary-slip"},
            ]
        )

    if role_set & _MANAGER_ROLES:
        cards.extend(
            [
                {"label": "Team Leave", "route": "/app/leave-application"},
                {"label": "Team Attendance", "route": "/app/attendance"},
            ]
        )

    if role_set & _HR_ROLES:
        cards.extend(
            [
                {"label": "Employees", "route": "/app/employee"},
                {"label": "Payroll", "route": "/app/payroll-entry"},
            ]
        )

    if "erpnext" in app_set and role_set & (_HR_ROLES | _MANAGER_ROLES | {"Projects User"}):
        cards.append({"label": "Projects", "route": "/app/project"})
    if "helpdesk" in app_set and role_set & (_EMPLOYEE_ROLES | _HR_ROLES | _MANAGER_ROLES):
        cards.append({"label": "Helpdesk", "route": "/helpdesk"})
    if "lms" in app_set and role_set & (_EMPLOYEE_ROLES | _HR_ROLES | _MANAGER_ROLES):
        cards.append({"label": "Learning", "route": "/lms"})
    if "india_payroll" in app_set and role_set & _HR_ROLES:
        cards.append({"label": "India Payroll", "route": "/app/payroll-entry"})

    return cards
