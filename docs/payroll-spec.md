# Payroll Spec and Employee Tax Deduction Notes

This document records decisions about the payroll spec format and per-employee payroll tax deductions storage.

## Employee-level fields (stored in `employee.payroll_tax_deductions`)

Use a flexible dict to store TD1 and other payroll-related values that vary per-employee.
Recommended keys:
- `td1_fed`: dict with federal TD1 values, e.g. `{"basic_personal_amount": 15000, "additional_amount": 0}`
- `td1_prov`: dict with provincial TD1 values
- `dependents`: integer count
- `additional_amounts`: list or dict of labeled additional tax amounts claimed by employee
- `exempt`: bool (true if employee is exempt from income tax withholding)

These fields are intentionally generic to support different jurisdictions and future additions.

## Payroll spec top-level notes
- `cpp` should include both employee and employer rates and the year-specific pensionable earnings max.
- Add `cpp2` as a placeholder for supplemental contributions if a jurisdiction requires it.
- Always verify rates and limits against official sources (CRA, Service Ontario, etc.) before activating a spec for payroll runs.

## Migration plan
- A migration script (`scripts/migrate_add_employee_payroll_tax_deductions.py`) is included to add the `payroll_tax_deductions` column to existing tenant DBs.
- For production DBs, prefer a proper migration tool (Alembic) and careful rollout.

## Auto-seeding payroll specs
- When a new company tenant DB is created, the system will auto-load any YAML files found under `seed/payroll/` (excluding `template.yml`) into the tenant `payroll_spec` table.
- To override or provide a single default spec file, set the environment variable `DEFAULT_PAYROLL_SPEC_YML` to the YAML path (e.g., `seed/payroll/payroll_spec_canada_ontario_2026.yml`).
- For manual seeding, use `scripts/seed_all_payroll_specs.py --company-id <id>` or `scripts/seed_payroll_spec.py --company-id <id> --yml <file>`.
