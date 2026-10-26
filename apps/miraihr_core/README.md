# MiraiHR Core

MiraiHR Core provides a fallback logo hook and small app-logo sizing rules through
Frappe's supported hooks. Product name, logo, favicon, theme, and navigation should
use native Frappe site settings and Workspaces. Frappe authorization remains
responsible for access to every module and record.

## Current status

Targets the Frappe v16 API range (`>=16.50,<17`) based on upstream package metadata. No site installation has been run in this workspace. The license declaration is intentionally unresolved pending legal review of the selected upstream combination; do not distribute this app until that review is complete.

The app does not implement HR workflows, custom navigation, authentication, or tenant
authorization. Frappe v16's `brand_html` is a Website Settings field, not an app hook;
the app intentionally does not define it. The supported `app_logo_url` hook is a
fallback. Website Settings and Navbar Settings take precedence and must be configured
on the site.
