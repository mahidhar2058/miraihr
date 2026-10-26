# Upstream repository inventory

**Checked:** 2026-10-26. The ten selected upstream repositories are registered as Git submodules under `upstream/`; the MiraiHR tree records each exact locked commit as a gitlink. A submodule is a pinned reference, not vendored upstream history. The exact source is reproduced by a recursive clone or `git submodule update --init --recursive`. Local source, remote, clean-tree, license-file, and pinned-SHA evidence is produced by `python scripts/verify_upstream_sources.py`. This does not prove runtime coexistence; installation and migration remain pending GitHub Actions.

| Project | Canonical source | Pinned submodule checkout | Compatibility / install | Status |
|---|---|---|---|---|
| Frappe | https://github.com/frappe/frappe | `upstream/frappe` — v16.53.0, `e8d41dd0061a32ee781caefe5d0b0d2bb7c15362` | Python >=3.14,<3.15; Node >=24 | Candidate; runtime install pending |
| ERPNext | https://github.com/frappe/erpnext | `upstream/erpnext` — v16.52.1, `ade850bbd6a7412e9994a9637d2c5c713771632a` | Frappe >=16.50,<17 | Candidate; runtime install pending |
| HRMS | https://github.com/frappe/hrms | `upstream/hrms` — v16.52.0, `5c72c067c0a3bcc969a49c708b7bec545a046fe9` | Frappe/ERPNext >=16.50,<17 | Candidate; runtime install pending |
| India Payroll | https://github.com/frappe/india-payroll | `upstream/india-payroll` — v16.0.4, `2f033e4a37931ec6859d81b84b60666511665bba` | Frappe/ERPNext/HRMS >=16,<17 | Candidate; issue #134 regression gate |
| Helpdesk | https://github.com/frappe/helpdesk | `upstream/helpdesk` — v1.31.0, `7d7e394e7571fbdbdda04a65a279566b0ac9ce7f` | Frappe >=15.123.1,<17; requires Telephony | Candidate; runtime install pending |
| LMS | https://github.com/frappe/lms | `upstream/lms` — v2.64.0, `7c46bb8f4976222b3f6aa84368551c424edaa194` | Frappe >=15.121,<17; requires Payments | Candidate; runtime install pending |
| Telephony | https://github.com/frappe/telephony | `upstream/telephony` — `9447577500a25d242088398157b72c654fa34b20` | No release tags; exact commit required by Helpdesk | Candidate; validate with Helpdesk |
| Payments | https://github.com/frappe/payments | `upstream/payments` — `cca07d9f9392e2ea0e521c5975151db9e4b6c321` | No release tags; exact commit required by LMS | Candidate; validate with LMS |
| frappe_docker | https://github.com/frappe/frappe_docker | `upstream/frappe_docker` — v4.0.1, `2b26e9ab8d751e5ea33bb7b930aea3550bb81ded` | Official Docker build patterns; no MiraiHR image built yet | Pinned source checkout |
| Helm | https://github.com/frappe/helm | `upstream/helm` — chart v8.0.73, `e930266e11ebbe37348ab9079fb0e75ab7d253ff` | Chart appVersion v16.32.1 lags candidate app versions | Pinned source checkout; chart not rendered |
| Gantt | https://github.com/frappe/gantt | Not cloned; optional source inspection | ERPNext upstream integration; no custom replacement planned | Deferred |
| Lending | https://github.com/frappe/lending | Not cloned; optional source inspection | Develop metadata requires Frappe/ERPNext >=17 | Excluded from this phase |
| Press | https://github.com/frappe/press | Not cloned; optional source inspection | Operator platform; independently validate if needed | Deferred |

### Reproducing the pinned sources

Fresh checkout:

```powershell
git clone --recurse-submodules https://github.com/mahidhar2058/miraihr.git
```

Existing checkout:

```powershell
git submodule update --init --recursive
```

Then verify the checked-out source and gitlinks:

```powershell
python scripts/verify_upstream_sources.py
```

The submodule entries expose navigable links and pin the selected upstream revisions in MiraiHR commits. They do not copy upstream file history into MiraiHR. CI installation/migration/workflow evidence, payroll regression results, transitive SBOM, separate-site API guarantees, and operational support SLAs remain unverified. The source gate verifies source identity and license evidence; it does not approve commercial redistribution or discharge GPL/AGPL obligations.
