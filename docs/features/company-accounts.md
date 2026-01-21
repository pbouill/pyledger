# Company accounts (bank, credit cards, loans)

Status: todo

Summary
-------
Manage company accounts, their balances, transactions, and reconciliation.

Goals
-----
- Create account types (bank, credit card, loan, cash)
- Support manual transaction creation and import (CSV/OFX)
- Provide reconciliation flows and balance checks

Data model ideas
----------------
- Account(id, company_id, name, type, currency, balance)
- Transaction(id, account_id, date, amount, description, metadata_json)

API & UX
--------
- CRUD for accounts
- Transaction import endpoint
- Reconciliation UI

Tests & Acceptance
------------------
- Import sample CSV/OFX and verify transactions are persisted and balances updated correctly.
