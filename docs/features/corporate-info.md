# Corporate information (minutes book, shareholders / cap table)

Status: todo

Summary
-------
Store corporate governance information: minutes, shareholder registry, share classes and cap table.

Goals
-----
- Record minutes and resolutions with timestamps and attachments
- Track shareholders, share classes, ownership percentages, and issuance history

Data model ideas
----------------
- Shareholder(id, company_id, name, contact)
- ShareClass(id, company_id, name, rights_json)
- ShareAllocation(id, shareholder_id, class_id, quantity, issued_at)

API & UX
--------
- Views for cap table and ownership changes
- Export cap table CSV for legal/filing purposes

Tests & Acceptance
------------------
- Creating share issuances updates cap table and ownership percentages.
