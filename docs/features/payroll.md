# Payroll & Employees

Status: todo

Summary
-------
Employee management and payroll processing, including generation of remittances for government taxes and contributions.

Goals
-----
- Employee profiles with tax identifiers and payment preferences
- Payroll runs (periodic), payslip generation, and posting of relevant accounting entries
- Auto-generation of remittance bills/payments for tax authorities

Data model ideas
----------------
- Employee(id, company_id, name, tax_id, bank_details_json, employment_start)
- PayrollRun(id, company_id, period_start, period_end, total_gross, total_net, status)
- Payslip(id, payrollrun_id, employee_id, gross, net, taxes)

API & UX
--------
- Create payroll run, preview payslips, approve and post
- Export filing reports for local government formats and integrate with payment APIs

Tests & Acceptance
------------------
- Creating a payroll run produces expected payslips and accounting entries.
