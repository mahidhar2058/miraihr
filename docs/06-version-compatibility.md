# Version Compatibility

**Status:** P0 design baseline. **Reviewed:** 2026-10-26. Facts are marked VERIFIED, ASSUMED, or UNVERIFIED; no application feature is implemented in P0.

## Purpose and scope

This specification establishes the version compatibility decisions and P1 implementation gates for an independent, white-label HRMS SaaS based on supported Frappe applications. It excludes MiraiTeams, payment gateways, and P0 deployment.

## P1 v16 candidate set (2026-10-26)

| App | Candidate release | Declared constraint / evidence | Decision |
|---|---|---|---|
| Frappe | `v16.53.0` (`e8d41dd0061a32ee781caefe5d0b0d2bb7c15362`) | Python `>=3.14,<3.15`; Node `>=24` | Immutable candidate; install not run |
| ERPNext | `v16.52.1` (`ade850bbd6a7412e9994a9637d2c5c713771632a`) | Frappe v16 | Immutable candidate; install not run |
| HRMS | `v16.52.0` (`5c72c067c0a3bcc969a49c708b7bec545a046fe9`) | Frappe and ERPNext `>=16.50,<17` | Immutable candidate; install not run |
| India Payroll | `v16.0.4` (`2f033e4a37931ec6859d81b84b60666511665bba`) | Python >=3.14 and Frappe/ERPNext/HRMS `>=16,<17` | Immutable candidate; regression issue #134 is an open gate |
| Telephony | `develop` (`9447577500a25d242088398157b72c654fa34b20`) | Helpdesk dependency `>=0.0.1,<1`; no release tags | Immutable commit candidate; validate with Helpdesk |
| Helpdesk | `v1.31.0` (`7d7e394e7571fbdbdda04a65a279566b0ac9ce7f`) | Frappe `>=15.123.1,<17`; Telephony `>=0.0.1,<1` | Immutable candidate; install not run |
| Payments | `version-16` (`cca07d9f9392e2ea0e521c5975151db9e4b6c321`) | Frappe `>=16,<17`; Python >=3.14 | LMS dependency; no release tag, validate with LMS |
| Learning | `v2.64.0` (`7c46bb8f4976222b3f6aa84368551c424edaa194`) | Frappe `>=15.121,<17`; Payments `>=0.0.1,<1` | Immutable candidate; includes Payments dependency; install not run |
| Lending | Excluded from P1 installed set | Not required for initial release; exact same-site validation is deferred | Evaluate separately if scope changes |

This is a **machine-readable candidate lock**, not accepted compatibility. Full source SHAs, runtime constraints, license findings, dependency order, and the inspected ERPNext image digest are in [dependencies.lock.json](../deployment/dependencies.lock.json). Lock acceptance still requires building the combined pinned image, installing all apps, migrations, and functional smoke tests. Declared version ranges do not prove that the selected releases work together.

### Runtime and blocking validation

Frappe v16 requires Python 3.14 and Node.js 24+ per the official migration guide. This Windows host has Python 3.12.1 and Node 20.11.0; Bench and Helm are absent. Docker Engine 29.9.2 was accessible with authorized elevated invocation; its Linux engine has 8 CPUs and 7.6 GiB memory allocation. The host had about 3.4 GiB available memory and 75.2 GiB free disk. No images were pulled, containers started, or builds attempted. A remote `frappe/erpnext:v16` OCI manifest was inspected, including the amd64 digest; this does not verify the requested multi-app image. Bench initialization, application installation, migrations, Helm rendering, and app workflows remain NOT TESTED/BLOCKED. No Docker data was removed.

India Payroll issue [#134](https://github.com/frappe/india-payroll/issues/134), opened 2026-10-06, describes employer ESIC being overwritten with a full-month amount for prorated pay on a v16 stack. Until a regression case passes on the selected release, Indian payroll must not be represented as commercially ready.

## Previous P0 baseline

The earlier aligned v15 design was superseded because India Payroll v16 release metadata explicitly targets Frappe, ERPNext, and HRMS v16. Do not treat the old v15 matrix as current. The selected v16 refs above are candidates only until the full same-site install and workflow suite passes. Lending remains excluded because its current development metadata targets Frappe/ERPNext 17.

## Requirements and decisions

- **MHR-P0-06-01 — P0 specification; P1 implementation:** establish a reviewable design, measurable acceptance evidence, owner, dependencies, and phase mapping for version compatibility.
- Prefer supported upstream apps and extension hooks. Pin exact commits after integration tests; never infer compatibility from a shared framework alone.
- Default to one Frappe site/database per customer, mapped using immutable tenant UUIDs. Email domains are hints for discovery, never tenant authority.
- Separate operator registry and billing metadata from customer HR and payroll records; support access is narrow, time-limited, and audited.
- Meter distinct human billable employees per tenant per Asia/Kolkata calendar month from successful authenticated activity; deduplicate by tenant, canonical employee, and month; exclude service accounts. Preserve immutable month-end snapshots and append corrections. Contractual edge cases remain to be approved.
- SSO uses OIDC with issuer/audience/signature/state/nonce/redirect validation and issuer+subject mapping. Do not store corporate passwords. Maintain audited local break-glass access.
- Protect personal, payroll, and financial data with least privilege, encryption, tenant-scoped access, minimized logs, and tested backups.

## Evidence and status

Checked 2026-10-26. Current evidence identifies stable v15 and v16 streams, but does not establish one compatible release set for all requested apps. India Payroll v16 has a release; v15 compatibility remains UNVERIFIED. Helpdesk documents v15/v16 support in its README matrix, while its develop metadata requires v16 development. Treat LMS exact branch constraints and all commercial license obligations as UNVERIFIED pending tag-level inspection.

- Frappe and ERPNext release streams: https://github.com/frappe/frappe/releases and https://github.com/frappe/erpnext/releases
- HRMS branch policy: https://github.com/frappe/hrms/wiki/Changes-to-branching-and-versioning
- Helpdesk README compatibility matrix: https://github.com/frappe/helpdesk (main lists Frappe 15 and 16); develop pyproject: https://github.com/frappe/helpdesk/blob/develop/pyproject.toml (Frappe >=16 dev)
- India Payroll releases: https://github.com/frappe/india-payroll/releases (v16.0.0 observed; v15 compatibility unresolved)
- LMS repository/license metadata: https://github.com/frappe/lms (AGPL-3.0)
- Lending develop constraints: https://github.com/frappe/lending/blob/develop/pyproject.toml (Frappe and ERPNext >=17 dev)
- Docker and Helm: https://github.com/frappe/frappe_docker and https://github.com/frappe/helm
- HR mobile PWA guide: https://docs.frappe.io/hr/mobile-app-installation
- Press constraints: https://github.com/frappe/press/blob/develop/pyproject.toml (Frappe >=15,<17)

## Acceptance criteria

- **AC-06-01:** Requirement MHR-P0-06-01 maps to a P1 backlog item and a named verification artifact.
- **AC-06-02:** No unverified compatibility, legal, payroll, privacy, security, or capacity statement is represented as proven.
- **AC-06-03:** P1 proves role-based tenant isolation, with automated cross-tenant access-denial tests before release.

## Security, dependencies, and risks

Dependencies include the pinned Frappe ecosystem, identity provider, customer configuration, and hosting. Main risks are incompatible releases, payroll errors, tenant escape, missed/duplicate usage, copyleft obligations, upstream changes, and solo-operator capacity. See [threat model](25-security-threat-model.md), [compatibility](06-version-compatibility.md), and [risk register](40-risk-register.md).

## Open questions

- Which exact app tags pass a reproducible disposable-site install and upgrade test?
- What usage contract, retention, RPO/RTO, and support-access policy will customers approve?
- Which legal and statutory payroll reviews are required before commercial launch?
