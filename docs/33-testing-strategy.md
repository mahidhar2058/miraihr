# Testing Strategy

**Status:** P0 design plus P1 static and hosted CI configuration; hosted run pending. **Reviewed:** 2026-10-26. No runtime test result is claimed before GitHub Actions executes.

## Purpose and scope

This document records the test strategy for a white-label product assembled from supported Frappe applications. Service-backed tests run only on GitHub-hosted Ubuntu as local Docker/WSL/Kubernetes runtime is prohibited.

## Area-specific design

Test the small custom integration boundary and upstream applications. The configured P1 workflow covers source metadata, site creation, migrations, app test commands, native branding/assets, expected upstream workspaces and doctypes, and a synthetic Issue #134 payroll regression. Cross-tenant isolation, SSO claim abuse, usage metering, backup restore, and upgrade rollback remain future acceptance gates and are not covered by this workflow.

## P1 evidence status

Lightweight local validation performed to date includes Python syntax checks, JSON/TOML parsing, source/asset inspection, and `git diff --check`; these do not execute Frappe. GitHub Actions has not yet run. After a manual push, inspect workflow `MiraiHR P1 CI` and its artifacts. A failed install, migration, or test fails the integration job while preserving logs. Issue #134 fixture status must be PASS before payroll acceptance; it has not run. Cross-tenant, permission, SSO, browser interaction, and statutory payroll review remain required before commercial release.

## Requirements and decisions

- **MHR-P0-33-01 — P0 specification; P1 implementation:** establish a reviewable design, measurable acceptance evidence, owner, dependencies, and phase mapping for testing strategy.
- Prefer supported upstream apps and extension hooks. Pin exact commits after integration tests; never infer compatibility from a shared framework alone.
- Default to one Frappe site/database per customer, mapped using immutable tenant UUIDs. Email domains are hints for discovery, never tenant authority.
- Separate operator registry and billing metadata from customer HR and payroll records; support access is narrow, time-limited, and audited.
- Meter distinct human billable employees per tenant per Asia/Kolkata calendar month from successful authenticated activity; deduplicate by tenant, canonical employee, and month; exclude service accounts. Preserve immutable month-end snapshots and append corrections. Contractual edge cases remain to be approved.
- SSO uses OIDC with issuer/audience/signature/state/nonce/redirect validation and issuer+subject mapping. Do not store corporate passwords. Maintain audited local break-glass access.
- Protect personal, payroll, and financial data with least privilege, encryption, tenant-scoped access, minimized logs, and tested backups.

## Evidence and status

Checked 2026-10-26. The source pins and metadata are inventoried, but same-site installation and runtime behavior remain unverified until hosted Actions runs. The test fixture for Issue #134 exists and is pending execution.

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

- **AC-33-01:** Requirement MHR-P0-33-01 maps to a P1 backlog item and a named verification artifact.
- **AC-33-02:** No unverified compatibility, legal, payroll, privacy, security, or capacity statement is represented as proven.
- **AC-33-03:** P1 proves role-based tenant isolation, with automated cross-tenant access-denial tests before release.

## Security, dependencies, and risks

Dependencies include the pinned Frappe ecosystem, identity provider, customer configuration, and hosting. Main risks are incompatible releases, payroll errors, tenant escape, missed/duplicate usage, copyleft obligations, upstream changes, and solo-operator capacity. See [threat model](25-security-threat-model.md), [compatibility](06-version-compatibility.md), and [risk register](40-risk-register.md).

## Open questions

- Which exact app tags pass a reproducible disposable-site install and upgrade test?
- What usage contract, retention, RPO/RTO, and support-access policy will customers approve?
- Which legal and statutory payroll reviews are required before commercial launch?
