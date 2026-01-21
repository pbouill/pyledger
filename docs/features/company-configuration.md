# Company configuration

Status: todo

Summary
-------
Company-level settings and contact information used throughout the app.

Goals
-----
- Allow admins to configure company name, legal address, logo, primary contacts, tax/registry numbers, default currency and timezone.
- Provide UI for managing branding (logo, header/footer for invoices).

Non-goals
---------
- This doc does not cover billing/payment gateway account setup (separate feature).

Data model ideas
----------------
- Company(id, name, legal_name, tax_number, address_json, currency, timezone, logo_url, settings_json)

API & UX
--------
- GET /api/companies/{id}
- PATCH /api/companies/{id}
- POST /api/companies/{id}/logo (multipart)

Migrations
----------
- Add `company` table (if tenant DB) or extend common DB `company` table (single-tenant mode).

Tests / Acceptance
------------------
- Ensure company updates persist and appear on generated invoices and reports.
- Validate logo upload and proper storage.

Related docs/PRs
----------------
- 
