# Repository instructions

- Follow the active user phase. P0 was documentation-only; P1 authorizes the MiraiHR Core, reproducible build/deployment artifacts, validation workflows, and related documentation described by the current P1 assignment.
- Inspect branch, status, and remotes before edits. Preserve user changes. Never push, change remotes, delete unreviewed data, or commit secrets.
- Commit each validated increment with a Conventional Commit message, staging only files for that increment. If sandbox policy prevents `.git` writes, do not change ACLs; report the required authorized commit environment.
- Mark upstream claims VERIFIED, ASSUMED, UNVERIFIED, or BLOCKED, cite primary sources, and record check dates. A dependency declaration is only a compatibility candidate; installation, migration, and representative behavior must pass before compatibility is accepted.
- Never bypass Frappe authorization, CSRF protections, session checks, or tenant boundaries for branding convenience.
- Keep candidate dependency pins immutable. No floating `latest`, `main`, or `develop` references in production lock files. Do not deploy remotely or push to GitHub.
- Do not run Docker/Kubernetes workloads unless explicitly needed for a bounded test and resource/data impact has been checked. Never remove user containers, volumes, or data.
- Read relevant docs before touching a workstream; update requirements and evidence when implementation reveals a difference.
