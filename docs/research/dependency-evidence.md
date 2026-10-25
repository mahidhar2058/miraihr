# Dependency evidence

**Checked:** 2026-10-26. Application source SHAs are resolved, but the set remains unvalidated until a combined install and migration test passes.

| Evidence | Observation | Consequence |
|---|---|---|
| https://github.com/frappe/hrms/wiki/Changes-to-branching-and-versioning | HRMS branch must align with Frappe/ERPNext branch | No cross-major mixing |
| https://github.com/frappe/helpdesk/blob/v1.31.0/pyproject.toml | Helpdesk v1.31.0 declares Frappe >=15.123.1,<17 and Telephony >=0.0.1,<1 | Pin Telephony commit and test together |
| https://github.com/frappe/telephony | No release tags; develop commit pinned in lock | Candidate only; validate against Helpdesk and Frappe 16 |
| https://github.com/frappe/india-payroll/releases | v16.0.4 metadata requires Frappe, ERPNext, HRMS >=16,<17 and Python >=3.14 | Candidate; payroll regression fixture issue #134 remains open |
| https://github.com/frappe/lms/releases | v2.64.0 tagged metadata requires Frappe >=15.121,<17 and Payments >=0.0.1,<1 | Pin Payments and test LMS installation; AGPL-3.0-or-later |
| https://github.com/frappe/lending/blob/develop/pyproject.toml | Develop declares Frappe and ERPNext >=17 dev | Exclude from initial compatible set |
| https://github.com/frappe/press/blob/develop/pyproject.toml | Press develop declares Frappe >=15,<17 | Potential operator tooling; independently validate |

## P1 candidate evidence (2026-10-26)

| App | Exact tag/ref | Full commit SHA | Declared constraint |
|---|---|---|---|
| Frappe | `v16.53.0` | `e8d41dd0061a32ee781caefe5d0b0d2bb7c15362` | Python >=3.14,<3.15; Node >=24 |
| ERPNext | `v16.52.1` | `ade850bbd6a7412e9994a9637d2c5c713771632a` | Frappe 16 |
| HRMS | `v16.52.0` | `5c72c067c0a3bcc969a49c708b7bec545a046fe9` | Frappe/ERPNext >=16.50,<17 |
| India Payroll | `v16.0.4` | `2f033e4a37931ec6859d81b84b60666511665bba` | Frappe/ERPNext/HRMS >=16,<17; Python >=3.14 |
| Telephony | `develop` | `9447577500a25d242088398157b72c654fa34b20` | Frappe >=14.101,<=17-dev; no release tag |
| Helpdesk | `v1.31.0` | `7d7e394e7571fbdbdda04a65a279566b0ac9ce7f` | Frappe >=15.123.1,<17; Telephony >=0.0.1,<1 |
| Payments | `version-16` | `cca07d9f9392e2ea0e521c5975151db9e4b6c321` | Frappe >=16,<17; Python >=3.14 |
| LMS | `v2.64.0` | `7c46bb8f4976222b3f6aa84368551c424edaa194` | Frappe >=15.121,<17; Payments >=0.0.1,<1 |

Sources: [Frappe releases](https://github.com/frappe/frappe/releases), [ERPNext releases](https://github.com/frappe/erpnext/releases), [HRMS releases](https://github.com/frappe/hrms/releases), [India Payroll v16.0.4 metadata](https://raw.githubusercontent.com/frappe/india-payroll/v16.0.4/pyproject.toml), [Helpdesk v1.31.0 metadata](https://raw.githubusercontent.com/frappe/helpdesk/v1.31.0/pyproject.toml), [LMS v2.64.0 metadata](https://github.com/frappe/lms/blob/v2.64.0/pyproject.toml), [Payments v16 metadata](https://github.com/frappe/payments/blob/version-16/pyproject.toml), [Telephony metadata](https://github.com/frappe/telephony/blob/develop/pyproject.toml), [Frappe v16 migration prerequisites](https://github.com/frappe/frappe/wiki/Migrating-to-version-16).

**Status:** source refs are immutable candidates, not a production lock. The Docker CLI is available and a remote `frappe/erpnext:v16` manifest was inspected; no image layers were pulled or containers started. Bench/Helm are absent, Python/Node are below Frappe v16 requirements, and host memory headroom is about 3.4 GiB. Runtime installs, migrations, and workflows remain untested. See [machine-readable candidate lock](../../deployment/dependencies.lock.json).
