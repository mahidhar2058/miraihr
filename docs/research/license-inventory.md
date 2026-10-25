# License inventory

**Checked:** 2026-10-26. Preliminary source license review for selected candidates; this is not legal advice and does not determine the product's distribution obligations.

| Component | Preliminary finding | Required follow-up |
|---|---|---|
| Frappe | MIT at v16.52.0; selected v16.53.0 license still to verify | Preserve notice; inspect selected tag |
| ERPNext | GPL-3.0 at v16.52.0; selected v16.52.1 tag still to verify | Legal review of use, modifications, and distribution |
| HRMS | GPL-3.0 at v16.52.0 | Verify selected tag, preserve notices, review obligations |
| India Payroll | GPL-3.0 per upstream README; exact v16.0.4 license file not confirmed | Verify exact tag; payroll and copyleft review |
| Helpdesk | AGPL-3.0 repository metadata; verify v1.31.0 tag | Inspect exact tag and dependencies; review hosted modifications |
| Telephony | AGPL-3.0 repository metadata; no release tags | Verify pinned commit and review whether required features activate this app |
| LMS | AGPL-3.0-or-later at v2.64.0 | Review obligations; LMS pulls in Payments |
| Payments | License at pinned commit not yet confirmed | Verify before including LMS in commercial image |
| Frappe Docker / Helm | MIT | Preserve required notices |
| MiraiHR Core | `UNLICENSED`; no license has been granted | Owner/legal decision required before distribution |

No automated license scan or complete transitive SBOM has run. Do not distribute the combined image until exact-tag notices and transitive dependencies are reviewed by the owner and counsel.
