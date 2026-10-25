# Version Compatibility

**Status:** P0 design baseline. **Reviewed:** 2026-10-26. Facts are marked VERIFIED, ASSUMED, or UNVERIFIED; no application feature is implemented in P0.

## Purpose and scope

This specification establishes the version compatibility decisions and P1 implementation gates for an independent, white-label HRMS SaaS based on supported Frappe applications. It excludes MiraiTeams, payment gateways, and P0 deployment.

## P1 v16 candidate set (2026-10-26)

| App | Candidate release | Declared constraint / evidence | Decision |
|---|---|---|---|
| Frappe | `v16.53.0` (`e8d41dd`) | v16 release; Python `>=3.14,<3.15`; Node 24+ in v16 migration guide | Pin candidate |
| ERPNext | `v16.52.1` (`ade850b`) | v16 release; same major as Frappe | Pin candidate |
| HRMS | `v16.52.0` (`5c72c06`) | Frappe and ERPNext `>=16.50,<17` | Pin candidate |
| India Payroll | `v16.0.4` (`2f033e4`) | Tagged metadata requires Python >=3.14 and Frappe/ERPNext/HRMS `>=16,<17` | Pin candidate; payroll blocked on regression evidence |
| Helpdesk | `v1.31.0` (`7d7e394`) | Tagged metadata requires Frappe `>=15.123.1,<17` and Telephony `>=0.0.1,<1` | Pin candidate; Telephony transitive app still needs exact pin |
| Learning | `version-16` branch | Raw branch metadata requires Frappe `>=16,<17` and Payments `>=0.0.1,<1`; no exact commit captured | Do not include in image lock until commit and Payments are pinned |
| Lending | Excluded from P1 installed set | Not required for initial release; exact same-site validation is deferred | Evaluate separately if scope changes |

This is a **machine-readable candidate lock**, not accepted compatibility. Exact release tags and observed short commit prefixes are in [dependencies.lock.json](../deployment/dependencies.lock.json). Lock acceptance requires full commit resolution, image digests, Bench installation, module install, migrations, and functional smoke tests. The official branch metadata supports a plausible v16 combination, but does not prove the selected releases work together.

### Runtime and blocking validation

Frappe v16 requires Python 3.14 and Node.js 24+ per the official migration guide. This workstation has Python 3.12.1 and Node 20.11.0; Bench and Helm are absent. Docker is installed but the engine named pipe denies access; WSL also returns access denied. Therefore Bench initialization, installation, migration, container build, Helm rendering, and application smoke tests are BLOCKED here. Do not label the stack compatible until those gates run elsewhere.

India Payroll issue [#134](https://github.com/frappe/india-payroll/issues/134), opened 2026-10-06, describes employer ESIC being overwritten with a full-month amount for prorated pay on a v16 stack. Until a regression case passes on the selected release, Indian payroll must not be represented as commercially ready.

## Provisional matrix (not an install lock)

| Component | Candidate | Dependencies / install | Evidence and decision |
|---|---|---|---|
| Frappe | version-15 stable stream | Framework first; MariaDB/Redis and Bench | Stable v15 tags observed; exact pinned patch not selected |
| ERPNext | version-15 | Same major as Frappe | Stable v15 release stream; candidate |
| HRMS | version-15 | Frappe/ERPNext aligned | Official HRMS branch policy requires alignment; candidate |
| India Payroll | v16.0.0 release observed | HRMS integration; install after HRMS | v15 support unverified; BLOCKS final selection |
| Helpdesk | main has documented v15/v16 matrix | Frappe; exact tag required | Candidate; develop metadata is v16-dev and must not be used for v15 |
| LMS | exact release not chosen | Bench app; dependency range not recorded | UNVERIFIED; integration may be separate site/API |
| Lending | develop requires >=17-dev | ERPNext required | Exclude from MVP; separate API/partner evaluation later |
| Docker / Helm | official repos | Pin image digest and chart release | Deployment tools, not application compatibility proof |

**Decision:** no all-app same-site supported combination has been demonstrated. P1 must run a frozen, reproducible install/migrate/upgrade and cross-app acceptance suite. If India Payroll lacks a supported v15 release, evaluate a supported v16 stack as a whole; do not run payroll on a separate site without a documented identity, data, and reporting contract.

## Area-specific design

Provisional candidate is aligned Frappe/ERPNext/HRMS v15 plus compatible Helpdesk. India Payroll v16 release evidence prevents approving this matrix. LMS and exact tagged dependencies are unverified. P1 must freeze tag SHAs, runtime versions, install order, and migration evidence.

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
