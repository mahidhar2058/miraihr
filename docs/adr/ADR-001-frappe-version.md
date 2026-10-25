# ADR-001-frappe-version

**Status:** Candidate decision; runtime validation blocked. **Date:** 2026-10-26.

## Context and decision

Adopt the v16 release family as the candidate foundation: Frappe 16.53.0, ERPNext 16.52.1, HRMS 16.52.0, and India Payroll 16.0.4. Helpdesk 1.31.0 is a candidate. LMS remains excluded from the image lock until a commit and Payments dependency are pinned. This supersedes the P0 v15 candidate after tagged metadata showed India Payroll 16.0.4 depends on the matching v16 family. It is not an accepted production lock: Python 3.14/Node 24+ and an installation environment are unavailable, and an open ESIC prorating issue requires regression verification.

## Consequences and acceptance

Document trade-offs, owner, and unresolved risks in [decision log](../44-decision-log.md). Acceptance requires source evidence, traceable implementation tasks, and automated verification where applicable. No P0 code or deployment is authorized.
