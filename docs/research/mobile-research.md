# Mobile research

Official Frappe HR documentation states that HRMS v15 onward ships a mobile frontend installable as a PWA at `/hrms`. Android installation uses the browser install prompt; iOS uses Safari Add to Home Screen. Source: https://docs.frappe.io/hr/mobile-app-installation (checked 2026-10-26). Current integration status is **PWA candidate; not installed or tested**.

This establishes PWA access instructions, not app-store native packaging, offline parity, push notification guarantees, device compliance, or API support guarantees. P1 should test representative employee and manager journeys on supported Android Chrome and iOS Safari versions. Native Flutter/Capacitor wrappers remain an option requiring separate security, release, and maintenance assessment.
