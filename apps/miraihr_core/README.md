# MiraiHR Core

MiraiHR Core provides product branding and a role-aware Desk entry page using Frappe's hooks and standard Desk page APIs. It does not replace Frappe authorization: each destination remains protected by the upstream app's server-side permissions.

## Current status

Targets the Frappe v16 API range (`>=16.50,<17`) based on upstream package metadata. No site installation has been run in this workspace. The license declaration is intentionally unresolved pending legal review of the selected upstream combination; do not distribute this app until that review is complete.

The navigation page only links to modules that are both installed and allowed by the user's roles. It reads no employee, payroll, or tenant data.
