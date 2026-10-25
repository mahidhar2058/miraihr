# Frappe Press evaluation

Press is a possible future operator platform, not a P0 dependency. Its develop pyproject at https://github.com/frappe/press/blob/develop/pyproject.toml declares Frappe `>=15.0.0,<17.0.0` (checked 2026-10-26). This may make it a candidate for v15-based hosting, but does not establish compatibility with MiraiHR's apps or requirements. Evaluate provisioning, tenant isolation, billing data access, support model, upgrades, and license/deployment needs in P1. Do not assume Press provides the desired commercial control plane or compliant cross-tenant access.
