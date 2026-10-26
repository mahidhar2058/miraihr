# White Label Strategy

**Status:** P0 design baseline. **Reviewed:** 2026-10-26. Facts are marked VERIFIED, ASSUMED, or UNVERIFIED; no application feature is implemented in P0.

## Purpose and scope

This specification establishes the white label strategy decisions and P1 implementation gates for an independent, white-label HRMS SaaS based on supported Frappe applications. It excludes MiraiTeams, payment gateways, and P0 deployment.

## Area-specific design

Use custom app hooks, app assets, workspace configuration, translations, and supported themes. Brand assets may change logos/colors/labels while retaining attribution and required notices. Do not patch upstream source; regression-test every upgrade.

## P1 integration findings (2026-10-26)

Frappe v16 already supports product branding through Website Settings and Navbar Settings for app name/logo, favicon, theme, and navigation presentation. The supported `app_logo_url`, `app_include_css`, and `web_include_css` hooks are the small extension points retained by MiraiHR Core. `brand_html` is a Website Settings field, not a hook. Role-specific navigation should be configured with native Workspaces and Sidebar items; workspace visibility is not authorization, so upstream role and DocType permissions must enforce access. Core's custom landing page and navigation API were removed after reference checks confirmed they were self-contained.

No Frappe site has been installed, so login, Desk, email template, favicon, PWA, and workspace appearance are not yet validated. Configure title, logo, favicon, theme, and workspaces in the site after installation, and preserve upstream attribution and license notices.

## Requirements and decisions

- **MHR-P0-07-01 — P0 specification; P1 implementation:** establish a reviewable design, measurable acceptance evidence, owner, dependencies, and phase mapping for white label strategy.
- Prefer supported upstream apps and extension hooks. Pin exact commits after integration tests; never infer compatibility from a shared framework alone.
- Default to one Frappe site/database per customer, mapped using immutable tenant UUIDs. Email domains are hints for discovery, never tenant authority.
- Separate operator registry and billing metadata from customer HR and payroll records; support access is narrow, time-limited, and audited.
- Meter distinct human billable employees per tenant per Asia/Kolkata calendar month from successful authenticated activity; deduplicate by tenant, canonical employee, and month; exclude service accounts. Preserve immutable month-end snapshots and append corrections. Contractual edge cases remain to be approved.
- SSO uses OIDC with issuer/audience/signature/state/nonce/redirect validation and issuer+subject mapping. Do not store corporate passwords. Maintain audited local break-glass access.
- Protect personal, payroll, and financial data with least privilege, encryption, tenant-scoped access, minimized logs, and tested backups.

## Evidence and status

The source candidate set and exact constraints are recorded in [version compatibility](06-version-compatibility.md) and [dependency evidence](research/dependency-evidence.md). Branding support is confirmed in Frappe v16's `app_logo_url`, `app_include_css`, and `web_include_css` hooks and native Website/Navbar settings. The official HR mobile guide establishes an installable PWA, not native app-store packaging: https://docs.frappe.io/hr/mobile-app-installation.

## Acceptance criteria

- **AC-07-01:** Requirement MHR-P0-07-01 maps to a P1 backlog item and a named verification artifact.
- **AC-07-02:** No unverified compatibility, legal, payroll, privacy, security, or capacity statement is represented as proven.
- **AC-07-03:** P1 proves role-based tenant isolation, with automated cross-tenant access-denial tests before release.

## Security, dependencies, and risks

Dependencies include the pinned Frappe ecosystem, identity provider, customer configuration, and hosting. Main risks are incompatible releases, payroll errors, tenant escape, missed/duplicate usage, copyleft obligations, upstream changes, and solo-operator capacity. See [threat model](25-security-threat-model.md), [compatibility](06-version-compatibility.md), and [risk register](40-risk-register.md).

## Open questions

- Which exact app tags pass a reproducible disposable-site install and upgrade test?
- What usage contract, retention, RPO/RTO, and support-access policy will customers approve?
- Which legal and statutory payroll reviews are required before commercial launch?
