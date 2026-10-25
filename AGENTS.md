# Repository instructions

- Respect P0 scope: documentation only; do not implement features, run Docker/Kubernetes, deploy, push, or change remotes.
- Preserve user files and inspect Git status before edits. Never commit secrets or unrelated changes.
- Mark external claims VERIFIED, ASSUMED, UNVERIFIED, or BLOCKED and include primary source URLs and checked date.
- Do not claim compatibility without tag-level dependency evidence and an integrated install/upgrade test.
- Tenant isolation, payroll privacy, and upstream authorization are release blockers. Read [security](docs/25-security-threat-model.md) and [compatibility](docs/06-version-compatibility.md).
