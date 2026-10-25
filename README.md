# MiraiHR

MiraiHR is an independent, white-label, multi-tenant HRMS SaaS built by integrating mature Frappe applications. P1 is implementing MiraiHR Core and reproducible deployment foundations; MiraiTeams is outside this repository.

## Status

P1 has a v16 candidate lock based on exact upstream release tags. It is not yet installation- or payroll-validated. The local workstation currently lacks a usable Docker/WSL engine and the required Python 3.14 / Node 24 runtime. See [dependency candidate](deployment/dependencies.lock.json), [compatibility evidence](docs/06-version-compatibility.md), and [acceptance gates](docs/planning/acceptance-gates.md).

## Docs

Start with [project charter](docs/00-project-charter.md), [architecture](docs/04-system-architecture.md), [roadmap](docs/37-roadmap.md), [security](docs/25-security-threat-model.md), and the [MiraiHR Core app](apps/miraihr_core/README.md).
