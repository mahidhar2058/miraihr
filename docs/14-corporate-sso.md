# Corporate Sso

**Status:** P0 design baseline. **Reviewed:** 2026-10-26. Facts are marked VERIFIED, ASSUMED, or UNVERIFIED; no application feature is implemented in P0.

## Purpose and scope

This specification establishes the corporate sso decisions and P1 implementation gates for an independent, white-label HRMS SaaS based on supported Frappe applications. It excludes MiraiTeams, payment gateways, and P0 deployment.

## OIDC flow and lifecycle

Configure a separate Entra ID or Google Workspace OIDC client per tenant. Validate exact issuer, audience, signing keys, state, nonce, expiry, and pre-registered redirect URI; allow only approved email domains as an additional policy check, not tenant selection. Link on immutable `(issuer, subject)` after verified domain/HR employee mapping; do not silently merge accounts by email. JIT may create a pending identity but must not grant HR roles. Deactivation and role changes require explicit policy; SCIM is deferred. Keep local MFA-protected break-glass admin accounts with alerting and access review. Store client secrets in external secret storage and redact auth logs.

## Area-specific design

Configure tenant-specific Entra ID and Google OIDC clients; validate signature, issuer, audience, state, nonce, time, and redirect. Link by verified provider subject, avoid email-only account merges, map roles conservatively, support deactivation, and retain audited local break-glass.

## Requirements and decisions

- **MHR-P0-14-01 — P0 specification; P1 implementation:** establish a reviewable design, measurable acceptance evidence, owner, dependencies, and phase mapping for corporate sso.
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

- **AC-14-01:** Requirement MHR-P0-14-01 maps to a P1 backlog item and a named verification artifact.
- **AC-14-02:** No unverified compatibility, legal, payroll, privacy, security, or capacity statement is represented as proven.
- **AC-14-03:** P1 proves role-based tenant isolation, with automated cross-tenant access-denial tests before release.

## Security, dependencies, and risks

Dependencies include the pinned Frappe ecosystem, identity provider, customer configuration, and hosting. Main risks are incompatible releases, payroll errors, tenant escape, missed/duplicate usage, copyleft obligations, upstream changes, and solo-operator capacity. See [threat model](25-security-threat-model.md), [compatibility](06-version-compatibility.md), and [risk register](40-risk-register.md).

## Open questions

- Which exact app tags pass a reproducible disposable-site install and upgrade test?
- What usage contract, retention, RPO/RTO, and support-access policy will customers approve?
- Which legal and statutory payroll reviews are required before commercial launch?
