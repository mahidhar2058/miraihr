# License inventory

**Checked:** 2026-10-26. Preliminary source license review for selected candidates; this is not legal advice and does not determine the product's distribution obligations.

| Component | Preliminary finding | Required follow-up |
|---|---|---|
| Frappe v16.53.0 | MIT; `LICENSE` verified in pinned checkout | Preserve notice; inspect bundled dependencies |
| ERPNext v16.52.1 | GPL-3.0; `license.txt` verified in pinned checkout | Legal review of use, modifications, and distribution |
| HRMS v16.52.0 | GPL-3.0; `license.txt` verified in pinned checkout | Preserve notices; review obligations |
| India Payroll v16.0.4 | GPL-3.0; `license.txt` verified in pinned checkout | Payroll and copyleft review |
| Helpdesk v1.31.0 | AGPL-3.0; `LICENSE` verified in pinned checkout | Review hosted modifications and dependencies |
| Telephony pinned commit | AGPL-3.0; `license.txt` verified in pinned checkout | Required by Helpdesk metadata; assess obligations |
| LMS v2.64.0 | AGPL-3.0; license verified in pinned checkout | Review obligations; LMS pulls in Payments |
| Payments pinned commit | MIT; `LICENSE` verified in pinned checkout | Preserve notice |
| Frappe Docker v4.0.1 / Helm 8.0.73 | MIT; license files verified in pinned checkouts | Preserve required notices |
| MiraiHR Core | `UNLICENSED`; no license has been granted | Owner/legal decision required before distribution |

No automated license scan or complete transitive SBOM has run. Do not distribute the combined image until transitive dependencies are scanned and obligations are reviewed by the owner and counsel.
