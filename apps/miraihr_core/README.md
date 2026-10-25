# MiraiHR Core

MiraiHR Core provides product branding through Frappe's supported hooks. Employee,
manager, and HR navigation should use upstream Workspaces and Sidebar configuration.
Frappe authorization remains responsible for access to every module and record.

## Current status

Targets the Frappe v16 API range (`>=16.50,<17`) based on upstream package metadata. No site installation has been run in this workspace. The license declaration is intentionally unresolved pending legal review of the selected upstream combination; do not distribute this app until that review is complete.

The app does not implement HR workflows, custom navigation, authentication, or tenant
authorization. The logo and CSS assets are branding resources; product title and site
settings should be configured through native Frappe settings.
