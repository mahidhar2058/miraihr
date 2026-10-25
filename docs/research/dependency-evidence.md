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

## P1 candidate evidence (2026-10-26)

| App | Exact candidate tag | Observed release commit prefix | Declared constraint |
|---|---|---|---|
| Frappe | `v16.53.0` | `e8d41dd` | Python >=3.14,<3.15; Node >=24 in v16 migration guide |
| ERPNext | `v16.52.1` | `ade850b` | Frappe v16, Python >=3.14 |
| HRMS | `v16.52.0` | `5c72c06` | Frappe and ERPNext >=16.50,<17 |
| India Payroll | `v16.0.4` | `2f033e4` | Frappe, ERPNext, HRMS >=16,<17; Python >=3.14 |
| Helpdesk | `v1.31.0` | `7d7e394` | Frappe >=15.123.1,<17; Telephony >=0.0.1,<1 |
| Learning | version-16 branch (not pinned) | Not captured | Frappe >=16,<17; Payments >=0.0.1,<1 |

Sources: [Frappe release](https://github.com/frappe/frappe/releases), [ERPNext release](https://github.com/frappe/erpnext/releases), [HRMS release and metadata](https://github.com/frappe/hrms/releases), [India Payroll tagged metadata](https://raw.githubusercontent.com/frappe/india-payroll/v16.0.4/pyproject.toml), [Helpdesk tagged metadata](https://raw.githubusercontent.com/frappe/helpdesk/v1.31.0/pyproject.toml), [LMS v16 metadata](https://raw.githubusercontent.com/frappe/lms/version-16/pyproject.toml), [Frappe v16 migration prerequisites](https://github.com/frappe/frappe/wiki/Migrating-to-version-16).

**Status:** candidate only. Release commit prefixes are evidence, not full SHA locks. LMS and its Payments dependency and Helpdesk's Telephony dependency lack immutable pins in this repository. No disposable install/migration/functional validation could run because the workstation has Python 3.12/Node 20, no Bench/Helm, and Docker/WSL engine access is denied. No exact runtime image digest was obtainable. See [machine-readable candidate lock](../../deployment/dependencies.lock.json).
