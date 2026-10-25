# Dependency evidence

**Checked:** 2026-10-26. Evidence is insufficient for a complete lock.

| Evidence | Observation | Consequence |
|---|---|---|
| https://github.com/frappe/hrms/wiki/Changes-to-branching-and-versioning | HRMS branch must align with Frappe/ERPNext branch | No cross-major mixing |
| https://github.com/frappe/helpdesk | README matrix lists Helpdesk main with Frappe 15 and 16 | Candidate only; verify exact tag |
| https://github.com/frappe/helpdesk/blob/develop/pyproject.toml | Develop declares Frappe >=16 dev | Do not use develop with v15 |
| https://github.com/frappe/india-payroll/releases | v16.0.0 released | v15 pairing remains blocker |
| https://github.com/frappe/lending/blob/develop/pyproject.toml | Develop declares Frappe and ERPNext >=17 dev | Exclude from initial compatible set |
| https://github.com/frappe/press/blob/develop/pyproject.toml | Press develop declares Frappe >=15,<17 | Potential operator tooling; independently validate |

No exact compatible commit set is selected. P1 must resolve immutable tags, Python/Node/MariaDB/Redis constraints, install order, migration test, and reproducible SBOM before release.
