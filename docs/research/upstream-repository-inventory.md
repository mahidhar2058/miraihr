# Upstream repository inventory

**Checked:** 2026-10-26. Evidence below is repository metadata or official documentation; availability of tags does not prove runtime coexistence.

| Project | Canonical source | Current finding | Compatibility / install | Status |
|---|---|---|---|---|
| Frappe | https://github.com/frappe/frappe | Framework; v15 and v16 tags/releases visible | Bench app; lock exact tag | VERIFIED releases; selection pending |
| ERPNext | https://github.com/frappe/erpnext | ERP/accounting foundation | Align major branch with Frappe | VERIFIED release stream |
| HRMS | https://github.com/frappe/hrms | Employee lifecycle, payroll, leave, attendance; separate app | Official branch policy aligns HRMS branch with Frappe/ERPNext | VERIFIED policy |
| India Payroll | https://github.com/frappe/india-payroll | India statutory payroll integration; v16.0.0 release visible | v15 coexistence not confirmed | BLOCKED |
| Helpdesk | https://github.com/frappe/helpdesk | Customer service app with desk and portal | README matrix says main supports Frappe 15/16; develop pyproject says >=16 dev | VERIFIED declarations; exact tag pending |
| LMS | https://github.com/frappe/lms | Learning platform; repo metadata AGPL-3.0 | Bench install documented; exact framework range/tag pending | PARTIAL |
| Gantt | https://github.com/frappe/gantt | JS Gantt library used by ERPNext | Library integration; MIT metadata | VERIFIED function/license metadata |
| Lending | https://github.com/frappe/lending | Lending domain app | develop pyproject requires Frappe/ERPNext >=17 dev | Excluded MVP; future separate evaluation |
| frappe_docker | https://github.com/frappe/frappe_docker | Official container/deployment recipes; MIT | Build custom app image; pin image digest | VERIFIED repository |
| helm | https://github.com/frappe/helm | Chart with web, scheduler, Socket.IO, workers and provisioning jobs | Chart release/app versions must be pinned | VERIFIED chart capability |
| Press | https://github.com/frappe/press | Frappe Cloud operator platform | develop metadata Frappe >=15,<17; not assumed compatible with target lock | EVALUATE later |

**Unavailable from this inspection:** complete exact-tag source metadata for all projects, API guarantees between independently deployed sites, exact LMS dependency bounds, all transitive licenses, and operational support SLAs. These remain UNVERIFIED.
