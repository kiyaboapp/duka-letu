# Implementation Plan: Tailwind UI Overhaul

## Overview

Replace the broken Bootstrap/crispy-forms UI with a Tailwind CSS standalone implementation.
Work proceeds in order: static assets → form widget attrs → base layout → page templates.
No Node.js, no build step, no CDN. One downloaded CSS file, all templates hand-crafted.

## Tasks

- [x] 1. Set up Tailwind CSS static asset and remove Bootstrap files
  - Download the Tailwind CSS standalone CLI for Windows (`tailwindcss-windows-x64.exe`) from
    https://github.com/tailwindlabs/tailwindcss/releases/latest and place it in the project root
  - Run: `tailwindcss-windows-x64.exe --input /dev/null --output static/css/tailwind.css --minify`
    to generate `static/css/tailwind.css`
  - Delete `static/css/bootstrap.min.css`
  - Delete `static/js/bootstrap.bundle.min.js`
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Add Tailwind widget attrs to all three form files
  - [x] 2.1 Update `sales/forms.py` — add Tailwind `class` attr to every field widget in
    `SaleForm`, `ReturnInwardForm`, `SaleOfficeUseForm`, and `DrawingForm`
    - Standard class string: `mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm`
    - Date/datetime fields keep their `type` attr and gain the class attr
    - Select fields get the same class string
    - _Requirements: 4.1, 4.2, 4.5_

  - [ ]* 2.2 Write property test for sales form widget attrs (Property 6)
    - **Property 6: Tailwind widget attrs present on all form fields**
    - **Validates: Requirements 4.2, 4.5**
    - For each field in SaleForm, ReturnInwardForm, SaleOfficeUseForm, DrawingForm assert
      `field.widget.attrs['class']` contains `mt-1 block w-full rounded-md border-gray-300`

  - [x] 2.3 Update `credit/forms.py` — add Tailwind `class` attr to every field widget in
    `DebtorForm`, `DebtForm`, and `DebtReturnForm`
    - Same class string as above; date fields keep `type` attr
    - _Requirements: 4.1, 4.3, 4.5_

  - [ ]* 2.4 Write property test for credit form widget attrs (Property 6)
    - **Property 6: Tailwind widget attrs present on all form fields**
    - **Validates: Requirements 4.3, 4.5**
    - For each field in DebtorForm, DebtForm, DebtReturnForm assert widget attrs contain the class

  - [x] 2.5 Update `inventory/forms.py` — add Tailwind `class` attr to every field widget in
    `PurchaseForm`, `PurchaseDetailForm`, and `ReturnOutwardForm`
    - Same class string; date fields keep `type` attr
    - _Requirements: 4.1, 4.4, 4.5_

  - [ ]* 2.6 Write property test for inventory form widget attrs (Property 6)
    - **Property 6: Tailwind widget attrs present on all form fields**
    - **Validates: Requirements 4.4, 4.5**
    - For each field in PurchaseForm, PurchaseDetailForm, ReturnOutwardForm assert widget attrs

- [x] 3. Replace `templates/base.html` with dark sidebar Tailwind layout
  - Remove all inline `<style>` blocks and Bootstrap classes from base.html
  - Reference `static/css/tailwind.css` via `{% load static %}` / `{% static 'css/tailwind.css' %}`
  - Implement fixed dark sidebar (`bg-gray-900 w-64 flex-shrink-0`) with nav groups:
    Dashboard, Sales, Credit Sales, Inventory, Products, Finance, Assets, Reports, Admin
  - Active nav item: `bg-blue-600 text-white`; inactive: `text-gray-300 hover:bg-gray-800 hover:text-white`
  - Active state detection via `request.resolver_match.app_name`
  - Top header bar with page title area and hamburger button for mobile
  - Mobile: sidebar hidden below `md` breakpoint, toggled by inline JS (no external library)
  - Flash messages rendered with tag-to-color mapping:
    success → `bg-green-50 border-green-200 text-green-800`,
    error → `bg-red-50 border-red-200 text-red-800`,
    warning → `bg-yellow-50 border-yellow-200 text-yellow-800`,
    info → `bg-blue-50 border-blue-200 text-blue-800`
  - Template blocks: `title`, `content`, `extra_css`, `extra_js`
  - _Requirements: 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 3.1 Write property test for active nav exclusivity (Property 1)
    - **Property 1: Active navigation state is exclusive**
    - **Validates: Requirement 2.3**
    - Render base.html for each app_name; assert exactly one nav link has `bg-blue-600` and all
      others have `text-gray-300`

  - [ ]* 3.2 Write property test for flash message color mapping (Property 2)
    - **Property 2: Flash message color mapping is exhaustive**
    - **Validates: Requirement 2.4**
    - For each tag in [success, error, warning, info] render base.html with a message; assert the
      correct color class set is present and no message is rendered without a color class

  - [ ]* 3.3 Write property test for no Bootstrap classes in base.html (Property 3)
    - **Property 3: No Bootstrap classes in any template**
    - **Validates: Requirements 2.5, 3.3**
    - Read base.html source; assert zero occurrences of `col-md-`, `d-flex`, `btn btn-`,
      `table table-`, `badge bg-`, `row g-`, `container`

  - [ ]* 3.4 Write property test that base.html is extended by all non-PDF templates (Property 4)
    - **Property 4: All non-PDF templates extend base.html**
    - **Validates: Requirement 3.2**
    - For each template file in Template_Set except PDF_Template, assert source starts with
      `{% extends 'base.html' %}` and contains `{% block content %}`

- [x] 4. Checkpoint — Ensure base.html renders without errors
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Replace dashboard template
  - Replace `templates/dashboard/index.html` — remove all Bootstrap/crispy classes
  - Page header: `<h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>` + date display
  - Four KPI cards (Today's Revenue, Transactions Today, Month to Date, Outstanding Receivables)
    using the KPI_Card component with circular icon, `tabular-nums` value, and label
  - Alerts panel: overdue debts, low stock, out of stock, overdue obligations using
    red/yellow badge-style alerts; "No alerts" fallback text
  - Recent Sales table using Data_Table component with empty-state row
  - Low Stock Items table (conditional) using Data_Table component
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2_

- [x] 6. Replace sales templates
  - [x] 6.1 Replace `templates/sales/index.html`
    - Page header with "+ New Sale" accent button
    - KPI summary row (today's sales count, today's revenue, MTD revenue)
    - Recent sales Data_Table: product, qty, amount (`tabular-nums`), payment method, time
    - Empty-state row when no sales
    - _Requirements: 3.1–3.6, 5.1, 5.2, 5.4_

  - [x] 6.2 Replace `templates/sales/sale_list.html`
    - Page header with "+ New Sale" button
    - Data_Table: date, product, qty, unit price, amount, payment method, actions (Details small-action button)
    - `tabular-nums` on all numeric/amount columns
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.4_

  - [x] 6.3 Replace `templates/sales/sale_form.html`
    - Remove `{% load crispy_forms_tags %}` and `{{ form|crispy }}`
    - Render each form field manually using the Form Field component pattern
      (`{{ field }}` with label, required star, error messages in `text-red-600`)
    - Cancel (secondary button) and Save Sale (primary button) actions
    - _Requirements: 3.3, 3.4, 3.5, 4.5, 4.6, 5.4_

  - [x] 6.4 Replace `templates/sales/return_inward_form.html`
    - Same manual field rendering pattern as sale_form.html
    - Cancel and Save Return buttons
    - _Requirements: 3.3, 3.4, 3.5, 4.5, 4.6, 5.4_

  - [ ]* 6.5 Write property test for no Bootstrap classes in sales templates (Property 3)
    - **Property 3: No Bootstrap classes in any template**
    - **Validates: Requirements 3.3, 2.5**
    - Assert zero Bootstrap class occurrences in all four sales template files

- [x] 7. Replace inventory templates
  - [x] 7.1 Replace `templates/inventory/index.html`
    - Page header with "+ New Purchase" button
    - KPI cards: total purchases, total stock value, low stock count
    - Recent purchases Data_Table with empty-state row
    - _Requirements: 3.1–3.6, 5.1, 5.2, 5.4_

  - [x] 7.2 Replace `templates/inventory/purchase_list.html`
    - Page header with "+ New Purchase" button
    - Data_Table: date, supplier, invoice number, total cost, actions
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.4_

  - [x] 7.3 Replace `templates/inventory/purchase_form.html`
    - Remove `{% load crispy_forms_tags %}` and all `{{ form|crispy }}` / `{{ formset|crispy }}`
    - Render purchase header fields manually (supplier, purchase_date, invoice_number)
    - Render formset management form + each PurchaseDetailForm row manually in a bordered container
    - Cancel and Save Purchase buttons
    - _Requirements: 3.3, 3.4, 3.5, 4.5, 4.6, 5.4_

  - [ ]* 7.4 Write property test for no Bootstrap classes in inventory templates (Property 3)
    - **Property 3: No Bootstrap classes in any template**
    - **Validates: Requirements 3.3, 2.5**
    - Assert zero Bootstrap class occurrences in all three inventory template files

- [x] 8. Replace credit templates
  - [x] 8.1 Replace `templates/credit/index.html`
    - Page header with "+ New Debtor" and "+ Credit Sale" buttons
    - KPI cards: total debtors, total outstanding, overdue count
    - Debtors summary Data_Table with empty-state row
    - _Requirements: 3.1–3.6, 5.1, 5.2, 5.4_

  - [x] 8.2 Replace `templates/credit/debtor_list.html`
    - Page header with "+ New Debtor" button
    - Data_Table: name, phone, total debt, outstanding balance, actions (Details small-action button)
    - `tabular-nums` on amount columns; empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.4_

  - [x] 8.3 Replace `templates/credit/debtor_detail.html`
    - Page header with debtor name + "+ Credit Sale" and "Record Repayment" buttons
    - Info card: phone, address
    - KPI cards: Total Debt, Outstanding Balance
    - Credit sales Data_Table: ID, product, amount due, balance, expected date, status Badge
    - Badge variants: Overdue → red, Paid → green, Active → yellow
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.3, 5.4_

  - [x] 8.4 Replace `templates/credit/debtor_form.html`
    - Manual field rendering for DebtorForm (name, address, phone_1, phone_2, nida_id)
    - Cancel and Save buttons
    - _Requirements: 3.3, 3.4, 3.5, 4.5, 4.6, 5.4_

  - [x] 8.5 Replace `templates/credit/debt_form.html`
    - Manual field rendering for DebtForm
    - Cancel and Save Credit Sale buttons
    - _Requirements: 3.3, 3.4, 3.5, 4.5, 4.6, 5.4_

  - [x] 8.6 Replace `templates/credit/debt_return_form.html`
    - Manual field rendering for DebtReturnForm
    - Cancel and Save Repayment buttons
    - _Requirements: 3.3, 3.4, 3.5, 4.5, 4.6, 5.4_

  - [ ]* 8.7 Write property test for no Bootstrap classes in credit templates (Property 3)
    - **Property 3: No Bootstrap classes in any template**
    - **Validates: Requirements 3.3, 2.5**
    - Assert zero Bootstrap class occurrences in all six credit template files

  - [ ]* 8.8 Write property test for Badge color variants (Property 8)
    - **Property 8: Badge color variants are exhaustive and exclusive**
    - **Validates: Requirement 5.3**
    - Parse debtor_detail.html; for each badge element assert it carries exactly one of the four
      defined color variant class pairs and no Bootstrap badge class

- [x] 9. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Replace finance and assets templates
  - [x] 10.1 Replace `templates/finance/index.html`
    - Page header "Finance"
    - KPI cards: total obligations, overdue obligations, paid this month
    - Obligations Data_Table with status Badge (Overdue → red, Paid → green, Pending → gray)
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.1, 5.2, 5.3, 5.4_

  - [x] 10.2 Replace `templates/assets/index.html`
    - Page header "Assets"
    - KPI cards: total assets, total book value
    - Assets Data_Table: name, category, purchase date, cost, book value
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.1, 5.2, 5.4_

  - [ ]* 10.3 Write property test for no Bootstrap classes in finance/assets templates (Property 3)
    - **Property 3: No Bootstrap classes in any template**
    - **Validates: Requirements 3.3, 2.5**
    - Assert zero Bootstrap class occurrences in finance/index.html and assets/index.html

- [x] 11. Create and replace catalog templates
  - [x] 11.1 Create `templates/catalog/index.html` (new file)
    - Page header "Catalog" with link to product list
    - Summary KPI cards: total products, total SKUs, low stock SKUs
    - _Requirements: 3.1–3.5, 3.7, 5.1, 5.4_

  - [x] 11.2 Replace `templates/catalog/product_list.html`
    - Page header "Products"
    - Data_Table: product name, spec, current stock, reorder level, status Badge
    - Badge: OK → green, Low Stock → yellow, Out of Stock → red
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.3, 5.4_

  - [x] 11.3 Replace `templates/catalog/product_detail.html`
    - Page header with product name
    - Info card: category, description
    - SKUs Data_Table: spec value, current stock, reorder level, suggested price, status Badge
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.3, 5.4_

  - [ ]* 11.4 Write property test for no Bootstrap classes in catalog templates (Property 3)
    - **Property 3: No Bootstrap classes in any template**
    - **Validates: Requirements 3.3, 2.5**
    - Assert zero Bootstrap class occurrences in all three catalog template files

- [x] 12. Replace reports templates
  - [x] 12.1 Replace `templates/reports/index.html`
    - Page header "Reports"
    - Navigation cards/links to: Income Statement, Stock Report, Debtor Aging
    - _Requirements: 3.1–3.5, 5.4_

  - [x] 12.2 Replace `templates/reports/income_statement.html`
    - Page header "Income Statement" with period filter buttons (Month/Quarter/Year) and Export PDF button
    - Active period button: `bg-blue-600 text-white`; inactive: secondary variant
    - Accounting table: REVENUE section, COGS section, GROSS PROFIT row
    - Section headers as full-width gray rows; subtotal rows in distinct background
    - All amounts `tabular-nums`; negative amounts in `text-red-600`
    - _Requirements: 3.1–3.5, 5.2, 5.4_

  - [x] 12.3 Replace `templates/reports/income_statement_pdf.html` (PDF template)
    - Standalone HTML document — does NOT extend base.html
    - Own `<html>`, `<head>`, `<body>` tags
    - Print-safe inline CSS only (no sidebar, no header, no JS)
    - Accounting table matching income_statement.html structure
    - No Bootstrap classes
    - _Requirements: 3.3, 6.1, 6.2, 6.3, 6.4_

  - [x] 12.4 Replace `templates/reports/stock_report.html`
    - Page header "Stock Report"
    - Out-of-stock and low-stock summary alerts using Flash_Message-style alert components
    - Data_Table: product, spec, stock, reorder level, status Badge
    - Badge: OK → green, Low Stock → yellow, Out of Stock → red
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.3, 5.4_

  - [x] 12.5 Replace `templates/reports/debtor_aging.html`
    - Page header "Debtor Aging"
    - Data_Table: debtor name, 0–30 days, 31–60 days, 61–90 days, 90+ days, total outstanding
    - All amount columns `tabular-nums`; overdue buckets in `text-red-600`
    - Empty-state row
    - _Requirements: 3.1–3.6, 5.2, 5.4_

  - [ ]* 12.6 Write property test for no Bootstrap classes in reports templates (Property 3)
    - **Property 3: No Bootstrap classes in any template**
    - **Validates: Requirements 3.3, 2.5**
    - Assert zero Bootstrap class occurrences in all five reports template files

  - [ ]* 12.7 Write property test for empty-state rows (Property 5)
    - **Property 5: Empty-state row present for empty querysets**
    - **Validates: Requirement 3.6**
    - For each list-view template, render with an empty queryset and assert the Data_Table contains
      a `<td colspan="...">` element with non-empty descriptive text

- [x] 13. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- All form templates render fields manually via `{{ field }}` — never `{{ form|crispy }}`
- The PDF template (task 12.3) is the only template that does not extend base.html
- Property tests validate universal correctness; unit tests validate specific examples
- Tailwind CSS file must exist at `static/css/tailwind.css` before running the Django dev server
