# Upstream repository inventory

**Checked:** 2026-10-26. Evidence below is repository metadata or official documentation; availability of tags does not prove runtime coexistence. A v16 candidate stack supersedes the initial P0 v15 assumption, but remains unvalidated.

| Project | Canonical source | Current finding | Compatibility / install | Status |
|---|---|---|---|---|
| Frappe | https://github.com/frappe/frappe | Framework; candidate `v16.53.0`, release prefix `e8d41dd` | Bench app; Python 3.14, Node 24+ | Candidate; runtime unavailable |
| ERPNext | https://github.com/frappe/erpnext | ERP/accounting foundation; candidate `v16.52.1`, prefix `ade850b` | Align with Frappe 16 | Candidate; runtime unavailable |
| HRMS | https://github.com/frappe/hrms | Employee lifecycle, payroll, leave, attendance; candidate `v16.52.0`, prefix `5c72c06` | Metadata requires Frappe/ERPNext >=16.50,<17 | Candidate; runtime unavailable |
| India Payroll | https://github.com/frappe/india-payroll | India statutory payroll; candidate `v16.0.4`, prefix `2f033e4` | Tagged metadata requires Frappe/ERPNext/HRMS v16 | Candidate; issue #134 payroll regression blocker |
| Helpdesk | https://github.com/frappe/helpdesk | Customer service app; candidate `v1.31.0`, prefix `7d7e394` | Tagged metadata allows Frappe 15.123.1–16.x; requires Telephony | Candidate; Telephony not pinned |
| LMS | https://github.com/frappe/lms | Learning platform; AGPL-3.0 repository metadata | version-16 branch allows Frappe 16; requires Payments; exact commit not pinned | Blocked from locked image |
| Gantt | https://github.com/frappe/gantt | JS Gantt library used by ERPNext | Library integration; MIT metadata | VERIFIED function/license metadata |
| Lending | https://github.com/frappe/lending | Lending domain app | develop pyproject requires Frappe/ERPNext >=17 dev | Excluded MVP; future separate evaluation |
| frappe_docker | https://github.com/frappe/frappe_docker | Official container/deployment recipes; MIT | Build custom app image; pin image digest | VERIFIED repository |
| helm | https://github.com/frappe/helm | Chart with web, scheduler, Socket.IO, workers and provisioning jobs | Chart release/app versions must be pinned | VERIFIED chart capability |
| Press | https://github.com/frappe/press | Frappe Cloud operator platform | develop metadata Frappe >=15,<17; not assumed compatible with target lock | EVALUATE later |

**Unavailable from this inspection:** full commit SHAs and image digests, exact immutable LMS/Payments/Telephony pins, runtime install/migrate/functional test evidence, API guarantees between independently deployed sites, transitive licenses, and operational support SLAs. These remain UNVERIFIED.
