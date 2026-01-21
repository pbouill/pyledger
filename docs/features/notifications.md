# Notifications & Emailing

Status: todo

Summary
-------
Emailing invoices, notices, and scheduled reports using SMTP or third-party providers.

Goals
-----
- Template-based emails with variables
- Integration adapters for SMTP, SendGrid, SES (pluggable)
- Scheduled jobs to send periodic reports or reminders for overdue invoices

Data model ideas
----------------
- EmailTemplate(id, company_id, name, subject_template, body_template)
- OutboundEmail(id, company_id, to, template_id, status, sent_at, metadata_json)

API & UX
--------
- CRUD templates
- Send preview emails
- Dashboard for pending/sent emails and failures

Tests & Acceptance
------------------
- Template rendering and send path using a test SMTP or mock adapter.
