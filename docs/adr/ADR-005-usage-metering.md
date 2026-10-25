# ADR-005-usage-metering

**Status:** Proposed; review at P1 design gate. **Date:** 2026-10-26.

## Context and decision

Count distinct billable human employees with successful authenticated activity per tenant and Asia/Kolkata calendar month. Freeze immutable month-end snapshot; corrections append audit records. Contract details remain open.

## Consequences and acceptance

Document trade-offs, owner, and unresolved risks in [decision log](../44-decision-log.md). Acceptance requires source evidence, traceable implementation tasks, and automated verification where applicable. No P0 code or deployment is authorized.
