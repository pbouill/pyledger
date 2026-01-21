# Expenses & Bills

Status: todo

Summary
-------
Capture and manage company expenses: vendor bills, expense reports, attachments, recurring bills, and mileage tracking.

Goals
-----
- Create and categorize expenses/bills with attachments
- Track bill lifecycle: draft, sent, paid, overdue
- Create recurring bill templates and convert one-off bills to recurring
- Track mileage and support expense report submission and approval

Data model ideas
----------------
- Vendor(id, company_id, name, contact)
- Expense(id, company_id, vendor_id, category, amount, currency, date, attachments_json, status)
- RecurringTemplate(id, company_id, schedule, payload_json)

API & UX
--------
- Upload receipts/attachments and link to expenses
- UI for recurring bill schedules and converting one-off bills into templates

Reports
-------
- Expense summary by category, vendor, period
- Outstanding bills and payment aging

Tests & Acceptance
------------------
- Create recurring bill and ensure schedule triggers (or scheduled job stub) create new bills.
- Attachment upload and retrieval works.
