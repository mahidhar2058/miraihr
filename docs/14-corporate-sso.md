# Corporate Sso

**Status:** P0 design baseline. **Reviewed:** 2026-10-26. Facts are marked VERIFIED, ASSUMED, or UNVERIFIED; no application feature is implemented in P0.

## Purpose and scope

This specification establishes the corporate sso decisions and P1 implementation gates for an independent, white-label HRMS SaaS based on supported Frappe applications. It excludes MiraiTeams, payment gateways, and P0 deployment.

## OIDC flow and lifecycle

Configure a separate Entra ID or Google Workspace OIDC client per tenant. Validate exact issuer, audience, signing keys, state, nonce, expiry, and pre-registered redirect URI; allow only approved email domains as an additional policy check, not tenant selection. Link on immutable `(issuer, subject)` after verified domain/HR employee mapping; do not silently merge accounts by email. JIT may create a pending identity but must not grant HR roles. Deactivation and role changes require explicit policy; SCIM is deferred. Keep local MFA-protected break-glass admin accounts with alerting and access review. Store client secrets in external secret storage and redact auth logs.

## P1 upstream security review (2026-10-26)

Frappe v16 exposes native Social Login Key configuration for Google, Office 365, Keycloak, and custom OAuth providers. Source review of the built-in Office 365 flow found ID-token decoding with signature verification disabled and no tenant/issuer binding in the inspected login path. Therefore native provider availability alone does not meet MiraiHR's tenant-bound corporate SSO requirements. Entra/Google SSO is **BLOCKED pending a vetted secure integration and configured identity-provider test**. Do not enable JIT signup or link accounts by email alone. Local Frappe authentication remains a supported fallback during evaluation.

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

P1 source-review notes are recorded above. Frappe provides provider configuration, but the inspected v16 Office 365 login implementation did not demonstrate signature or tenant/issuer verification required by this design. Source: https://github.com/frappe/frappe/blob/version-16/frappe/utils/oauth.py. SSO remains unverified until an approved integration is configured and tested with a real provider.

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
