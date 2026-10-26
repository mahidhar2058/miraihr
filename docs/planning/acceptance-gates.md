# Acceptance gates

1. **P0 exit:** all requested docs present/nonempty, requirement IDs unique, links valid, source evidence dated, blockers visible. P0 baseline is committed at `869a35f8b4bdf0b5b800699c71ad4719078f253f`.
2. **P1 candidate lock:** candidate v16 tags, immutable full SHAs, transitive Telephony/Payments pins, LMS pin, and upstream image digest are recorded. Current status: source/metadata evidence is recorded; runtime lock acceptance and a MiraiHR image digest remain pending.
3. **P1 compatibility:** exact immutable app revisions install and migrate together in a disposable hosted environment; India payroll fixtures independently reviewed. Current status: PENDING GitHub Actions execution; local Docker/WSL/Kubernetes runtime is prohibited.
4. **Security:** automated tenant-isolation and authorization tests; threat review; secrets and dependency scans; no critical unresolved findings.
5. **Operational:** image provenance, staging rollout/rollback, encrypted backup and successful restore drill, alerts and runbooks.
6. **Pilot:** role-based browser acceptance, usage reconciliation, data protection review, support process and customer signoff.
