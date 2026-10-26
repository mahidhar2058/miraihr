# Github Actions Ci Cd

**Status:** P0 design plus P1 workflow implementation; hosted run pending. **Reviewed:** 2026-10-26. No workflow result is claimed before GitHub Actions executes.

## Purpose and scope

This document records the GitHub Actions workflow for a white-label product built from supported Frappe applications. Local Docker/WSL/Kubernetes and service-backed installations are prohibited; application runtime checks use GitHub-hosted runners. No production deployment or image publishing is configured.

## Area-specific design

Workflow `.github/workflows/ci-p1.yml` runs on pushes to `main`, pull requests targeting `main`, and manual dispatch. It has bounded jobs on `ubuntu-24.04`, read-only repository permissions, concurrency cancellation, and pinned third-party action SHAs. Its current jobs validate pinned source metadata, install the candidate applications in a disposable hosted Bench site with MariaDB/Redis, migrate and run application suites, check native branding and upstream workspaces, and run secret/image scans. It does not build a custom all-app image, render Helm, deploy, or publish.

## Implemented workflow evidence (pending first hosted run)

| Job | Work and commands | Artifacts | Timeout |
|---|---|---|---|
| `source-validation` | `validate_sources.py` fetches immutable SHAs and checks runtime/dependency/license metadata; validates branding hook/assets | `upstream-source-validation` | 30 min |
| `frappe-integration` | Hosted MariaDB 11.8.3 + Redis 7.4.2; Bench init, exact app checkout, requirements/assets, site creation, installs, migrate, `bench version`, site/workspace/branding HTTP checks, each app's `run-tests --app`, focused Issue #134 regression | `frappe-integration-evidence` (logs, results, license inventory, pip audit CycloneDX SBOM) | 300 min |
| `security` | Gitleaks history scan; Trivy HIGH/CRITICAL scan of the pinned upstream `frappe/erpnext` image digest | `upstream-base-image-security-scan` | 45 min |

These checks are configured, not passed. Runtime installation may expose incompatibilities; failures preserve logs and fail the job. Trivy currently scans the upstream base image only, not a MiraiHR all-app image. Artifact retention is 30 days. Estimated duration is bounded by the 300-minute integration timeout; no measured run time exists yet. Pull-request jobs receive no deployment credentials. The site/admin password is generated per run and is not a repository secret.

## Requirements and decisions

- **MHR-P0-30-01 — P0 specification; P1 implementation:** establish a reviewable design, measurable acceptance evidence, owner, dependencies, and phase mapping for github actions ci cd.
- Prefer supported upstream apps and extension hooks. Pin exact commits after integration tests; never infer compatibility from a shared framework alone.
- Default to one Frappe site/database per customer, mapped using immutable tenant UUIDs. Email domains are hints for discovery, never tenant authority.
- Separate operator registry and billing metadata from customer HR and payroll records; support access is narrow, time-limited, and audited.
- Meter distinct human billable employees per tenant per Asia/Kolkata calendar month from successful authenticated activity; deduplicate by tenant, canonical employee, and month; exclude service accounts. Preserve immutable month-end snapshots and append corrections. Contractual edge cases remain to be approved.
- SSO uses OIDC with issuer/audience/signature/state/nonce/redirect validation and issuer+subject mapping. Do not store corporate passwords. Maintain audited local break-glass access.
- Protect personal, payroll, and financial data with least privilege, encryption, tenant-scoped access, minimized logs, and tested backups.

## Evidence and status

Checked 2026-10-26. Exact candidate source revisions and metadata are recorded in `deployment/dependencies.lock.json` and `docs/research/upstream-repository-inventory.md`. Source compatibility is plausible from declared ranges; runtime coexistence remains unverified until the hosted workflow succeeds. Issue #134 remains a payroll acceptance gate. License obligations require legal review.

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

- **AC-30-01:** Requirement MHR-P0-30-01 maps to a P1 backlog item and a named verification artifact.
- **AC-30-02:** No unverified compatibility, legal, payroll, privacy, security, or capacity statement is represented as proven.
- **AC-30-03:** P1 proves role-based tenant isolation, with automated cross-tenant access-denial tests before release.

## Security, dependencies, and risks

Dependencies include the pinned Frappe ecosystem, identity provider, customer configuration, and hosting. Main risks are incompatible releases, payroll errors, tenant escape, missed/duplicate usage, copyleft obligations, upstream changes, and solo-operator capacity. See [threat model](25-security-threat-model.md), [compatibility](06-version-compatibility.md), and [risk register](40-risk-register.md).

## Open questions

- Which exact app tags pass a reproducible disposable-site install and upgrade test?
- What usage contract, retention, RPO/RTO, and support-access policy will customers approve?
- Which legal and statutory payroll reviews are required before commercial launch?
