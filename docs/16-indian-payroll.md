# Indian Payroll

**Status:** P0 design baseline. **Reviewed:** 2026-10-26. Facts are marked VERIFIED, ASSUMED, or UNVERIFIED; no application feature is implemented in P0.

## Purpose and scope

This specification establishes the indian payroll decisions and P1 implementation gates for an independent, white-label HRMS SaaS based on supported Frappe applications. It excludes MiraiTeams, payment gateways, and P0 deployment.

## Validation gate

Frappe HRMS provides payroll workflows; India Payroll release notes for v16 describe EPF, ESI, state professional tax, LWF, income-tax regimes, exemptions, marginal relief, and statutory registers. This is not proof that the rules are current for a given payroll period or that the app works with the candidate Frappe major. Before customer use, a qualified Indian payroll specialist must validate effective-date rules, state configuration, rounding, eligibility thresholds, sample salary slips, statutory registers, and amendment behavior against current authoritative rules. Never treat generated calculations as legal or tax advice. Payroll data stays within tenant site and private encrypted storage.

The selected candidate is India Payroll `v16.0.4`, whose tagged metadata declares Frappe/ERPNext/HRMS v16. However, upstream issue [#134](https://github.com/frappe/india-payroll/issues/134) reports an employer ESIC overstatement for partial-month pay on a v16 environment. A synthetic integration regression is now in `apps/miraihr_core/miraihr_core/tests/test_india_payroll_issue_134.py`; it asserts employer ESI is calculated from paid wages after recalculation. It has not run yet and makes no payroll readiness claim. No upstream code workaround is introduced here.

## Area-specific design

Reuse HRMS payroll and evaluate India Payroll for statutory deductions and reports. Validate payroll periods, effective-dated rule tables, state PT/LWF, PF/ESI eligibility, rounding, tax regime, declarations, arrears, and sample payslips with a qualified Indian payroll reviewer.

## Requirements and decisions

- **MHR-P0-16-01 — P0 specification; P1 implementation:** establish a reviewable design, measurable acceptance evidence, owner, dependencies, and phase mapping for indian payroll.
- Prefer supported upstream apps and extension hooks. Pin exact commits after integration tests; never infer compatibility from a shared framework alone.
- Default to one Frappe site/database per customer, mapped using immutable tenant UUIDs. Email domains are hints for discovery, never tenant authority.
- Separate operator registry and billing metadata from customer HR and payroll records; support access is narrow, time-limited, and audited.
- Meter distinct human billable employees per tenant per Asia/Kolkata calendar month from successful authenticated activity; deduplicate by tenant, canonical employee, and month; exclude service accounts. Preserve immutable month-end snapshots and append corrections. Contractual edge cases remain to be approved.
- SSO uses OIDC with issuer/audience/signature/state/nonce/redirect validation and issuer+subject mapping. Do not store corporate passwords. Maintain audited local break-glass access.
- Protect personal, payroll, and financial data with least privilege, encryption, tenant-scoped access, minimized logs, and tested backups.

## Evidence and status

The candidate revisions and checked-out upstream metadata are recorded in [dependency evidence](research/dependency-evidence.md) and the [repository inventory](research/upstream-repository-inventory.md). Version ranges allow the v16 candidate combination but do not demonstrate runtime compatibility. Local Docker/WSL testing is prohibited for this phase; GitHub-hosted Actions is the pending installation and regression environment.

## Acceptance criteria

- **AC-16-01:** Requirement MHR-P0-16-01 maps to a P1 backlog item and a named verification artifact.
- **AC-16-02:** No unverified compatibility, legal, payroll, privacy, security, or capacity statement is represented as proven.
- **AC-16-03:** P1 proves role-based tenant isolation, with automated cross-tenant access-denial tests before release.

## Security, dependencies, and risks

Dependencies include the pinned Frappe ecosystem, identity provider, customer configuration, and hosting. Main risks are incompatible releases, payroll errors, tenant escape, missed/duplicate usage, copyleft obligations, upstream changes, and solo-operator capacity. See [threat model](25-security-threat-model.md), [compatibility](06-version-compatibility.md), and [risk register](40-risk-register.md).

## Open questions

- Which exact app tags pass a reproducible disposable-site install and upgrade test?
- What usage contract, retention, RPO/RTO, and support-access policy will customers approve?
- Which legal and statutory payroll reviews are required before commercial launch?
