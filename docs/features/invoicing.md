# Invoicing

Status: todo

Summary
-------
Create, send, and track invoices and associated customer payments.

Goals
-----
- Create invoices from line items, taxes, discounts
- Track invoice states (draft, sent, paid, overdue)
- Record payments, partial payments, and refunds
- Issue credit notes

Data model ideas
----------------
- Customer(id, company_id, name, contact)
- Invoice(id, company_id, customer_id, state, total_amount, currency, due_date)
- InvoiceLine(id, invoice_id, description, qty, unit_price, tax_rate)
- Payment(id, invoice_id, amount, method, paid_at)

API & UX
--------
- Create/preview invoice UI
- Send via email (integration with notifications feature)
- Payment recording and reconciliation

Tests & Acceptance
------------------
- Issue invoice, mark as sent and then mark payment as received; ensure invoice state changes and accounting entries are recorded.
