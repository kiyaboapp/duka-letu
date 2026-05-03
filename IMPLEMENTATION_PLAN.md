# KIYABO DUKA — COMPLETE IMPLEMENTATION PLAN
# Date: 2026-05-03 | Stack: Django 6.0.4, SQLite, Tailwind, HTMX (local)

---

## GROUND TRUTH: CURRENT STATE

### App
- Django 6.0.4, Python 3.12, SQLite, Tailwind standalone binary
- manage.py check passes ✓
- No JS framework installed — HTMX must be downloaded locally
- reports/services/accounting.py — correct WAC engine ✓

### DB (real migrated data from MS Access)
| Table | Records |
|---|---|
| sales_sale | 4,025 |
| inventory_purchasedetail | 358 |
| credit_debt | 101 |
| credit_debtreturn | 191 |
| catalog_productspec | 90 |
| finance_paymentobligation | 106 |
| finance_payment | 28 |
| finance_paymentmethod | 4 (Cash, Mobile Payments, Bank Cheque, Cheque — name only) |
| finance_expensetype | 6 (Kodi, Mshahara, Umeme, Matangazo, Matengenezo, Usafi) |
| finance_expenseitem | 8 |
| assets_asset | 8 |

### DB schema gaps
| Table | Missing columns |
|---|---|
| catalog_productspec | cached_wac, cached_stock_value, budget_monthly_sales_qty |
| finance_paymentmethod | category_id, provider_id, clears_immediately, is_active |
| assets_asset | asset_reference, cost_price, acquisition_date, depreciation fields |
| reports_* | no tables at all |
| finance_budgetline | doesn't exist |
| finance_cashregistersession | doesn't exist |
| finance_sessionbalance | doesn't exist |
| finance_paymentcategory | doesn't exist |
| finance_paymentprovider | doesn't exist |

### What works
- Dashboard, catalog, inventory, sales, credit views — functional
- 3 report views: IncomeStatement, StockReport, DebtorAging
- Finance index (obligations list only)
- Assets index (list only)

### What's missing
- HTMX (not installed)
- django.contrib.humanize not in INSTALLED_APPS
- reports/views.py — only 3 views, needs 15 more
- finance/views.py — only index
- finance/urls.py — only index
- assets/views.py — only index
- reports/services/ — missing expenses.py, balance_sheet.py, cash_flow.py, sales_summary.py
- reports/periods.py, reports/forms.py, finance/forms.py, assets/forms.py — all missing
- finance/services.py — missing
- finance/management/commands/seed_payment_methods.py — missing
- All new report templates, all finance CRUD templates, all asset CRUD templates
- No self-sufficient pages — existing pages have no contextual actions

---

## CORE PRINCIPLE: SELF-SUFFICIENT, CONTEXTUAL PAGES

Every page must be a complete operational unit. The user should never need to navigate away
to perform a related action. Every model's detail page shows all related data and provides
inline actions for everything that can be done from that context.

### What "self-sufficient" means for each page:

**Product Detail (`/catalog/products/<pk>/`)**
- Shows: product info, all specs, current stock per spec, WAC, stock value
- Shows: recent sales (last 30 days), recent purchases, credit sales, office use
- Actions (inline, no page navigation):
  - [Sell] → HTMX dialog: pre-filled with this product, selling price, stock shown
  - [Record Purchase] → HTMX dialog: pre-filled with this product, supplier dropdown
  - [Record Credit Sale] → HTMX dialog: pre-filled with this product, debtor dropdown
  - [Record Office Use] → HTMX dialog: pre-filled with this product
  - [Record Drawing] → HTMX dialog: pre-filled with this product
- Links to: all sales for this product, all purchases for this product

**Sale List (`/sales/`)**
- Shows: today's sales by default, filterable by date/product/payment method
- Shows: today's total, by payment method breakdown
- Actions (inline):
  - [New Sale] → HTMX slide-in panel: product search → auto-fill price → submit
  - Each sale row: [Return] → HTMX dialog: pre-filled return inward form
- Links to: product detail for each item sold

**Debtor Detail (`/credit/debtors/<pk>/`)**
- Shows: debtor info (name, phone, NIDA), total owed, total paid, outstanding balance
- Shows: ALL debts with their individual balances, due dates, overdue status
- Shows: ALL repayments with dates and amounts
- Actions (inline, no page navigation):
  - [Record Repayment] on each debt row → HTMX inline form: pre-filled debt_id + balance
  - [New Credit Sale] → HTMX dialog: pre-filled with this debtor
  - [Block/Unblock] → HTMX toggle: one click, no page reload
- Links to: each product sold on credit

**Debtor List (`/credit/`)**
- Shows: all debtors with outstanding balance, overdue count, last activity
- Shows: total receivables, total overdue
- Actions (inline):
  - [Quick Repayment] on each row → HTMX dialog: debtor pre-filled, debt dropdown
- Links to: debtor detail

**Finance Index (`/finance/`)**
- Shows: overdue obligations (red), due this month (amber), upcoming (green)
- Shows: paid this month total
- Actions (inline, no page navigation):
  - [Pay] on each obligation row → HTMX inline form: pre-filled amount = balance
  - [Generate Obligations] → HTMX button: runs auto_generate_obligations(), refreshes list
- Links to: expense item detail for each obligation

**Expense Item Detail (`/finance/expenses/<pk>/`)**
- Shows: item info, current rate, recurrence pattern
- Shows: ALL obligations (paid/unpaid/overdue) with balances
- Shows: ALL payments made
- Actions (inline):
  - [Pay Latest Unpaid] → HTMX dialog: pre-filled with latest unpaid obligation
  - [Change Rate] → HTMX dialog: new rate form (preserves history)
  - [Activate/Deactivate] → HTMX toggle
- Links to: each payment, obligation detail

**Liability Detail (`/finance/liabilities/<pk>/`)**
- Shows: liability info, original amount, current balance, rate, maturity
- Shows: amortisation schedule (next 12 months)
- Shows: ALL payment history (principal + interest split)
- Actions (inline):
  - [Record Payment] → HTMX dialog: pre-filled principal + interest based on schedule
- Links to: each payment

**Asset Detail (`/assets/<pk>/`)**
- Shows: asset info, cost, acquisition date, depreciation method
- Shows: accumulated depreciation, net book value, monthly charge
- Shows: depreciation schedule (year by year)
- Actions (inline):
  - [Edit] → HTMX dialog: edit form
  - [Record Disposal] → HTMX dialog: disposal date + proceeds

**Purchase Detail (`/inventory/purchases/<pk>/`)**
- Shows: purchase header (supplier, date, invoice, carriage)
- Shows: ALL line items with product, qty, unit cost, amount
- Shows: total amount
- Actions (inline):
  - [Add Line Item] → HTMX inline form appended to table
  - [Return Item] on each line → HTMX dialog: return outward form pre-filled

**Dashboard (`/`)**
- Shows: today's revenue, MTD revenue, YTD revenue
- Shows: outstanding receivables, overdue debts count
- Shows: low stock count, out of stock count
- Shows: overdue obligations count
- Shows: recent sales (last 10)
- Shows: top products today
- Actions (inline):
  - [New Sale] → HTMX slide-in panel (same as sales list)
  - [View Low Stock] → links to /reports/low-stock/
  - [View Overdue] → links to /finance/ filtered to overdue

---

## IMPLEMENTATION PLAN — ORDERED BY DEPENDENCY

### PHASE 1 — Foundation

**1a. Download HTMX locally**
```bash
mkdir -p static/js
curl -sL https://unpkg.com/htmx.org@1.9.12/dist/htmx.min.js -o static/js/htmx.min.js
```
Add to base.html before </body>:
```html
<script src="{% static 'js/htmx.min.js' %}"></script>
```

**1b. settings.py**
- Add django.contrib.humanize to INSTALLED_APPS

**1c. apps/core/models.py** — TimestampedModel abstract base
```python
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
```
No migration needed (abstract).

---

### PHASE 2 — Model changes + migrations (manage.py check after each)

**2a. catalog/models.py** — ProductSpec:
- Add: cached_wac, cached_stock_value, budget_monthly_sales_qty
- Fix update_stock() to call refresh_wac() after saving
- Add refresh_wac() using ExpressionWrapper(F('quantity') * F('unit_cost')) — NOT Sum('amount')
- → makemigrations catalog → migrate

**2b. inventory/models.py**:
- Purchase: add carriage_inwards = DecimalField(default=0), notes = TextField(blank=True)
- PurchaseDetail: add delete() override to call spec.update_stock()
- → makemigrations inventory → migrate

**2c. sales/models.py**:
- Sale: add reference_number = CharField(blank=True, unique=True), auto-generate in save()
- Drawing: add drawing_type (GOODS/CASH), cash_amount = DecimalField(default=0), make product_spec nullable
- → makemigrations sales → migrate

**2d. credit/models.py**:
- Debt: add reference_number = CharField(blank=True, unique=True), payment_method FK (null)
- Debtor: add credit_limit = DecimalField(default=0), is_blocked = BooleanField(default=False)
- → makemigrations credit → migrate

**2e. finance/models.py** — keep all existing, add:
- ExpenseType: is_cogs = BooleanField(default=False), display_order = PositiveSmallIntegerField(default=0)
- Payment: payment_reference = CharField(blank=True, unique=True) auto-gen, approved_by = CharField(blank=True)
- LiabilityItem: interest_type (FLAT/REDUCING/NONE), monthly_interest_charge(), amortisation_schedule()
- NEW: PaymentCategory (code CASH/MOBILE_MONEY/BANK, name, display_order)
- NEW: PaymentProvider (FK→PaymentCategory, name, short_code, is_active)
- UPGRADE PaymentMethod: add category FK, provider FK (null), clears_immediately, is_active
- NEW: CashRegisterSession (session_date unique, opened_by, opening_float, status)
- NEW: SessionBalance (FK→Session, FK→PaymentMethod, physical_closing_balance, system_expected_balance, uncleared_amount)
- NEW: BudgetLine (financial_year, month, budget_type, FK→ExpenseType nullable, budgeted_amount)
- → makemigrations finance → migrate

**2f. assets/models.py** — major upgrade:
- Keep worth for backward compat
- Add: asset_reference (auto-gen FA-001), cost_price, acquisition_date
- Add: depreciation_method (SL/DB/NONE), depreciation_rate, residual_value
- Add: disposal_date, disposal_proceeds
- Add properties: accumulated_depreciation, net_book_value, annual_depreciation_charge, monthly_depreciation_charge
- → makemigrations assets → migrate

**2g. reports/models.py** — new:
- ReportSnapshot: report_code, period_start, period_end
- generated_by = CharField (NOT ForeignKey — no auth)
- locked_by = CharField(blank=True), locked_at, is_locked, data = JSONField, checksum
- lock(name: str) method
- → makemigrations reports → migrate

**2h. Seed + backfill:**
```bash
python manage.py seed_payment_methods
# backfill WAC for all 90 specs
# backfill asset_reference for all 8 assets
```

---

### PHASE 3 — Services

**3a. finance/services.py** — auto_generate_obligations()
- Idempotent, once per day via ObligationGeneratorLog
- Generates for current + next 2 months

**3b. reports/periods.py** — ReportPeriod + PRESET_CHOICES
- 10 presets + custom
- ReportPeriod.resolve(preset, start, end, default_preset, reference)

**3c. reports/services/expenses.py** — ExpenseService(start, end)
- by_type(), by_item(), total(), obligations_summary()
- Uses Sum('amount_paid') on Payment — real DB column ✓

**3d. reports/services/balance_sheet.py** — BalanceSheetService(as_of_date)
- inventory_value() — Sum('cached_stock_value')
- gross_receivables() — DB-level ExpressionWrapper on Debt/DebtReturn
- bad_debt_provision() — 10%/5%/1% by aging bucket
- net_book_value_assets() — from Asset properties
- current_liabilities() — Sum(F('amount_due') - F('prepayment_applied') - F('amount_paid'))
- closing_balance_by_type(method_type) — from CashRegisterSession.SessionBalance
- equity() = total_assets - total_liabilities
- to_balance_sheet() → full dict with equation check

**3e. reports/services/cash_flow.py** — CashFlowService(start, end)
- Indirect method: net_profit + depreciation + working capital changes
- All @property fields use ExpressionWrapper

**3f. reports/services/sales_summary.py** — DailySalesSummaryService(start, end)
- by_payment_method() — grouped by category code
- by_transaction_type() — ExpressionWrapper, NOT Sum('amount')
- top_products(limit), credit_sales_detail()

---

### PHASE 4 — Forms

**4a. reports/forms.py** — ReportPeriodForm
- preset ChoiceField, start/end DateFields
- resolved_period(default_preset) → ReportPeriod

**4b. finance/forms.py**
- ExpenseItemForm, ExpenseRateForm, PaymentForm, LiabilityPaymentForm

**4c. assets/forms.py**
- AssetForm — all fields including depreciation

**4d. sales/forms.py** — upgrade SaleForm
- product_spec: live search via HTMX (not a static dropdown)
- Auto-fill unit_price from default_selling_price on product select
- Show current stock badge
- Validate: qty <= current_stock

**4e. credit/forms.py** — upgrade DebtReturnForm
- debt: filtered to debtor's debts when debtor_id provided
- amount: pre-filled with debt.balance
- Validate: amount <= debt.balance

---

### PHASE 5 — Report views package + URLs

**reports/views/__init__.py** — EMPTY (no imports at module level — this was the bug before)

**reports/views/base.py** — BaseReportView
- Imports: from reports.forms import ReportPeriodForm (flat name)
- Imports: from reports.periods import ReportPeriod (flat name)
- get(request) → parse period → get_context() → render or PDF

**Individual view files** (all imports use flat names):
- income_statement.py — AccountingService + ExpenseService
- balance_sheet.py — BalanceSheetService (snapshot type)
- cash_flow.py — CashFlowService
- debtor_aging.py — inline aging logic
- daily_sales.py — DailySalesSummaryService
- stock_report.py — ProductSpec queryset
- expense_analysis.py — ExpenseService
- liability_schedule.py — LiabilityItem + LiabilityPaymentDetail
- drawings_summary.py — Drawing queryset
- purchase_summary.py — Purchase + PurchaseDetail
- product_profitability.py — ProductSpec + ExpressionWrapper
- budget_vs_actual.py — BudgetLine
- low_stock.py — ProductSpec filtered by stock <= reorder_level
- cash_reconciliation.py — CashRegisterSession
- snapshots.py — ReportSnapshot
- index.py — static quick links

**reports/urls.py** — all 15+ URLs

---

### PHASE 6 — Finance views + URLs (full CRUD + HTMX)

**finance/views.py** — expand:

index:
- Call auto_generate_obligations()
- Show overdue (red), due this month (amber), upcoming (green)
- Each obligation row has [Pay] button with HTMX
- [Generate Obligations] button refreshes the list

ExpenseItemListView:
- Searchable by name/type
- Filter by active/inactive
- Each row links to detail

ExpenseItemDetailView:
- Shows item info, current rate, recurrence pattern
- Shows all obligations (grouped: overdue/pending/paid)
- Shows all payments
- [Pay Latest Unpaid] HTMX dialog
- [Change Rate] HTMX dialog
- [Activate/Deactivate] HTMX toggle

ExpenseItemCreateView:
- Creates item + initial rate in one form

ExpenseRateCreateView:
- Adds new rate row (history preserved)

ObligationPayView:
- GET: returns HTMX partial with pre-filled payment form
- POST: records payment, updates obligation.amount_paid, returns updated row HTML

LiabilityListView:
- Shows all liabilities with current balance, next payment due

LiabilityDetailView:
- Shows liability info, amortisation schedule (next 12 months)
- Shows all payment history (principal + interest)
- [Record Payment] HTMX dialog pre-filled from schedule

LiabilityPaymentCreateView:
- Creates Payment + LiabilityPaymentDetail
- Returns HTMX partial on success

**finance/urls.py** — all URLs including HTMX endpoints:
- /finance/ — index
- /finance/expenses/ — list
- /finance/expenses/new/ — create
- /finance/expenses/<pk>/ — detail
- /finance/expenses/<pk>/rate/ — add rate
- /finance/expenses/<pk>/toggle/ — activate/deactivate
- /finance/obligation/<pk>/pay/ — HTMX pay endpoint
- /finance/liabilities/ — list
- /finance/liabilities/<pk>/ — detail
- /finance/liabilities/<pk>/pay/ — HTMX pay endpoint

---

### PHASE 7 — Assets views + URLs

**assets/views.py** — expand:

index:
- List all assets grouped by category
- Shows total cost, total accumulated depreciation, total NBV
- Each row links to detail

AssetDetailView:
- Shows all asset info
- Shows depreciation schedule (year by year until fully depreciated)
- Shows monthly charge
- [Edit] HTMX dialog
- [Record Disposal] HTMX dialog

AssetCreateView, AssetUpdateView, AssetDeleteView

**assets/urls.py** — all URLs

---

### PHASE 8 — Upgrade existing views for self-sufficiency

**catalog/views.py** — ProductSpecDetailView:
- Add HTMX endpoints for inline actions:
  - /catalog/products/<pk>/sell/ — returns sale form partial pre-filled
  - /catalog/products/<pk>/purchase/ — returns purchase form partial pre-filled
  - /catalog/products/<pk>/credit-sale/ — returns debt form partial pre-filled
  - /catalog/products/<pk>/office-use/ — returns office use form partial pre-filled
- Product detail page shows all related transactions with links

**credit/views.py** — DebtorDetailView:
- Add HTMX endpoint: /credit/debtors/<pk>/repay/<debt_pk>/ — returns repayment form partial
- Debtor detail shows all debts with individual [Repay] buttons
- Each debt shows its repayment history inline

**sales/views.py** — SaleListView:
- Add HTMX endpoint: /sales/sale/create/partial/ — returns sale panel HTML
- Sale list shows today's total by payment method
- Each sale row has [Return] button → HTMX return inward form

**dashboard/views.py**:
- Add [New Sale] button → same HTMX sale panel
- All KPI cards link to relevant detail pages

---

### PHASE 9 — Templates (complete, no placeholders)

All templates: {% extends "base.html" %}, {% load humanize %}, Tailwind CSS
TZS formatting: |floatformat:0|intcomma

**HTMX pattern used throughout:**
```html
<!-- Trigger inline form -->
<button hx-get="/finance/obligation/{{ o.pk }}/pay/"
        hx-target="#obligation-row-{{ o.pk }}"
        hx-swap="outerHTML"
        class="...">Pay</button>

<!-- The row itself has the id -->
<tr id="obligation-row-{{ o.pk }}">...</tr>

<!-- View returns partial HTML for HTMX, full page for direct access -->
def obligation_pay(request, pk):
    if request.method == 'GET':
        # Return form partial
        template = 'finance/_obligation_pay_form.html' if request.headers.get('HX-Request') else 'finance/payment_form.html'
    if request.method == 'POST':
        # Process, return updated row partial
        template = 'finance/_obligation_row.html' if request.headers.get('HX-Request') else redirect(...)
```

**Base report template:** templates/reports/base_report.html
**Period selector partial:** templates/reports/_period_selector.html

**Report templates (15):**
- daily_sales.html
- balance_sheet.html
- cash_flow.html
- expense_analysis.html
- debtor_aging.html (upgrade existing)
- liability_schedule.html
- drawings_summary.html
- purchase_summary.html
- product_profitability.html
- budget_vs_actual.html
- low_stock.html
- cash_reconciliation.html
- snapshot_list.html
- snapshot_detail.html
- income_statement.html (upgrade existing)

**Finance templates:**
- expense_list.html — searchable table, each row links to detail
- expense_detail.html — full detail with inline pay, rate change, toggle
- expense_form.html — create/edit
- rate_form.html — add rate (HTMX partial + full page)
- payment_form.html — pay obligation (HTMX partial + full page)
- _obligation_row.html — HTMX partial: single obligation row
- _obligation_pay_form.html — HTMX partial: inline pay form
- liability_list.html
- liability_detail.html — amortisation schedule + payment history + inline pay
- liability_payment_form.html — HTMX partial + full page

**Asset templates:**
- asset_form.html
- asset_detail.html — depreciation schedule + inline edit/disposal
- asset_confirm_delete.html
- _asset_edit_form.html — HTMX partial
- _asset_disposal_form.html — HTMX partial

**Catalog templates (upgrade):**
- product_detail.html — add inline action buttons with HTMX
- _sell_form.html — HTMX partial: sale form pre-filled with product
- _purchase_form.html — HTMX partial: purchase form pre-filled
- _credit_sale_form.html — HTMX partial: debt form pre-filled

**Credit templates (upgrade):**
- debtor_detail.html — add inline repayment per debt row
- _repay_form.html — HTMX partial: repayment form pre-filled with debt balance
- _debt_row.html — HTMX partial: single debt row (updated after repayment)

**Sales templates (upgrade):**
- sale_list.html — add HTMX sale panel
- _sale_panel.html — HTMX partial: full sale entry panel with product search

---

### PHASE 10 — Management commands + integrity

**finance/management/commands/seed_payment_methods.py**
- Creates PaymentCategory (CASH, MOBILE_MONEY, BANK)
- Creates PaymentProvider (Vodacom, Tigo, Airtel, CRDB, NMB, NBC)
- Creates PaymentMethod (Cash, M-Pesa, Tigo Pesa, Airtel Money, CRDB Transfer, CRDB Cheque, NMB Transfer, NMB Cheque)
- Maps existing 4 DB payment methods to new structure

**reports/management/commands/verify_accounting_integrity.py**
- Checks Opening + Net Purchases = COGS + Closing for every ProductSpec
- Reports violations with TZS amounts
- Checks cached_stock_value matches computed closing

---

## EXECUTION ORDER

```
1a  curl -sL https://unpkg.com/htmx.org@1.9.12/dist/htmx.min.js -o static/js/htmx.min.js
1b  settings.py — add humanize + HTMX static
1c  apps/core/models.py — TimestampedModel
2a  catalog/models.py + makemigrations catalog + migrate
2b  inventory/models.py + makemigrations inventory + migrate
2c  sales/models.py + makemigrations sales + migrate
2d  credit/models.py + makemigrations credit + migrate
2e  finance/models.py + makemigrations finance + migrate
2f  assets/models.py + makemigrations assets + migrate
2g  reports/models.py + makemigrations reports + migrate
2h  seed_payment_methods + backfill WAC + backfill asset refs
3   All services
4   All forms (including upgraded sale + debt return forms)
5   reports/views/ package + reports/urls.py
6   finance/views.py + finance/urls.py (full CRUD + HTMX)
7   assets/views.py + assets/urls.py (full CRUD + HTMX)
8   Upgrade catalog, credit, sales, dashboard views for self-sufficiency
9   All templates (complete — every page self-sufficient)
10  Management commands + verify_accounting_integrity
```

---

## NON-NEGOTIABLE RULES

1. manage.py check after every Phase 2 step — stop if it fails
2. All imports: flat names — from finance.models import, from catalog.models import
3. Coalesce always from django.db.models.functions
4. Never Sum('amount') — always Sum(ExpressionWrapper(F('quantity') * F('unit_price') - F('discount'), output_field=DecimalField()))
5. reports/views/__init__.py is EMPTY — no imports at module level
6. ReportSnapshot.generated_by is CharField — no ForeignKey(User)
7. HTMX served from static/js/htmx.min.js via {% static %}
8. Every template complete — zero placeholders, zero TODO comments
9. Payment method filtering always by category.code — never by name string
10. balance on PaymentObligation is @property — use F('amount_due') - F('prepayment_applied') - F('amount_paid') in ORM
11. amount on Sale/Debt/Drawing is @property — always use ExpressionWrapper in aggregations
12. Every view that serves HTMX partials also works as a full page (check HX-Request header)
13. Every detail page shows ALL related data and provides inline actions for everything possible
14. No form opens a new page if it can be done inline — use HTMX dialogs/panels

---

## SELF-SUFFICIENCY MATRIX

| Page | Shows | Inline Actions | Links To |
|---|---|---|---|
| Dashboard | Revenue KPIs, receivables, stock alerts, obligations, recent sales | New Sale panel | Sales list, Finance, Reports |
| Product Detail | Info, all specs, stock, WAC, recent transactions | Sell, Purchase, Credit Sale, Office Use, Drawing | Sales for product, Purchases for product |
| Sale List | Sales with filter, today's total by method | New Sale panel, Return on each row | Product detail |
| Debtor List | All debtors, outstanding balance, overdue count | Quick Repayment dialog | Debtor detail |
| Debtor Detail | Info, all debts with balances, all repayments | Repay per debt row, New Credit Sale, Block/Unblock | Product detail for each debt |
| Finance Index | Overdue/due/upcoming obligations | Pay per row, Generate Obligations | Expense item detail |
| Expense Detail | Info, rate history, recurrence, all obligations, all payments | Pay latest, Change rate, Toggle active | Each payment |
| Liability Detail | Info, balance, amortisation schedule, payment history | Record Payment | Each payment |
| Asset Detail | Info, depreciation schedule, NBV | Edit, Record Disposal | — |
| Purchase Detail | Header, all line items, totals | Add line item, Return per line | Product detail for each item |
| Reports Index | All reports grouped by frequency | — | Each report |
| Each Report | Period selector, full data, PDF button | — | Related detail pages |
