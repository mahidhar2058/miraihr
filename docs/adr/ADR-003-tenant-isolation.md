# ADR-003-tenant-isolation

**Status:** Proposed; review at P1 design gate. **Date:** 2026-10-26.

## Context and decision

Default to one Frappe site/database per customer, keyed by immutable tenant UUID. Separate infrastructure may share compute only with validated boundaries. Do not treat domains as tenant authority.

## Consequences and acceptance

Document trade-offs, owner, and unresolved risks in [decision log](../44-decision-log.md). Acceptance requires source evidence, traceable implementation tasks, and automated verification where applicable. No P0 code or deployment is authorized.
