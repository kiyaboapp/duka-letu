# KIYABO DUKA — COMPLETION TASK LIST
## Branch: feature/complete-implementation-plan
## Created: 2026-05-03

---

## EXECUTIVE SUMMARY

**Current State:**
- ✅ Django 6.0.4 installed, migrations applied
- ✅ HTMX downloaded locally (static/js/htmx.min.js)
- ✅ Payment methods seeded (11 methods across 3 categories)
- ✅ Core models exist with recent upgrades (PaymentCategory, PaymentProvider, etc.)
- ✅ Report services partially implemented (accounting.py, balance_sheet.py, cash_flow.py, expenses.py, sales_summary.py)
- ✅ Report views package structure created (18 view files in reports/views/)
- ✅ TimestampedModel abstract base created in apps/core/

**Missing (Critical Path):**
- ❌ Models NOT using TimestampedModel base (all models still inherit from models.Model directly)
- ❌ ProductSpec missing: cached_wac, cached_stock_value fields + refresh_wac() method
- ❌ finance/services.py MISSING (auto_generate_obligations not implemented)
- ❌ reports/forms.py MISSING (ReportPeriodForm not implemented)
- ❌ finance/forms.py MISSING (all forms)
- ❌ assets/forms.py MISSING
- ❌ sales/forms.py NOT upgraded (no HTMX live search, no auto-fill)
- ❌ credit/forms.py NOT upgraded (no debt filtering)
- ❌ Most report views are stubs — need full implementation
- ❌ Finance views: only index exists, no CRUD, no HTMX endpoints
- ❌ Assets views: only index exists, no detail, no disposal
- ❌ Catalog/Sales/Credit views: NO self-sufficient inline actions
- ❌ Templates: 70 templates exist but NONE have HTMX inline actions
- ❌ django.contrib.humanize NOT in INSTALLED_APPS

---

## PHASE-BY-PHASE TASK BREAKDOWN

### PHASE 1 — Foundation (PARTIAL ✓)

| # | Task | Status | Priority |
|---|------|--------|----------|
| 1a | Download HTMX locally | ✅ DONE | - |
| 1b | Add django.contrib.humanize to INSTALLED_APPS | ❌ TODO | P0 |
| 1c | Verify TimestampedModel exists | ✅ DONE | - |
| 1d | Make ALL models inherit from TimestampedModel | ❌ TODO | P0 |

**Action for 1d:** Update these files to import and use TimestampedModel:
- catalog/models.py (8 models)
- inventory/models.py (4 models)
- sales/models.py (6 models)
- credit/models.py (3 models)
- finance/models.py (10+ models)
- assets/models.py (1 model)
- reports/models.py (1 model)

---

### PHASE 2 — Model Enhancements + Migrations

| # | Task | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 2a | ProductSpec: add cached_wac, cached_stock_value | ❌ TODO | P0 | ExpressionWrapper for stock_value |
| 2b | ProductSpec: add refresh_wac() method | ❌ TODO | P0 | Call in update_stock() |
| 2c | Purchase: add carriage_inwards, notes | ⚠️ CHECK | P1 | May already exist |
| 2d | PurchaseDetail: add delete() override | ❌ TODO | P0 | Must call spec.update_stock() |
| 2e | Sale: add reference_number (auto-gen) | ⚠️ CHECK | P1 | May already exist |
| 2f | Drawing: add drawing_type, cash_amount | ⚠️ CHECK | P1 | May already exist |
| 2g | Debt: add reference_number, payment_method FK | ⚠️ CHECK | P1 | May already exist |
| 2h | Debtor: add credit_limit, is_blocked | ⚠️ CHECK | P1 | May already exist |
| 2i | ExpenseType: add is_cogs, display_order | ❌ TODO | P1 | For P&L ordering |
| 2j | Payment: add payment_reference, approved_by | ⚠️ CHECK | P1 | May already exist |
| 2k | LiabilityItem: add interest_type, amortisation_schedule() | ❌ TODO | P1 | FLAT/REDUCING/NONE |
| 2l | Asset: verify all depreciation fields exist | ⚠️ CHECK | P1 | Check migration 0002 |
| 2m | Run makemigrations + migrate | ❌ TODO | P0 | After all model changes |
| 2n | Backfill WAC for all ProductSpecs | ❌ TODO | P0 | Management command or shell |
| 2o | Backfill asset_reference for all Assets | ❌ TODO | P1 | If missing |

---

### PHASE 3 — Services Layer

| # | Task | Status | Priority | File |
|---|------|--------|----------|------|
| 3a | finance/services.py: auto_generate_obligations() | ❌ TODO | P0 | Idempotent, ObligationGeneratorLog |
| 3b | reports/periods.py: ReportPeriod class + PRESET_CHOICES | ❌ TODO | P0 | 10 presets + custom |
| 3c | reports/services/expenses.py: ExpenseService | ⚠️ EXISTS | P1 | Verify completeness |
| 3d | reports/services/balance_sheet.py: BalanceSheetService | ⚠️ EXISTS | P1 | Verify completeness |
| 3e | reports/services/cash_flow.py: CashFlowService | ⚠️ EXISTS | P1 | Verify completeness |
| 3f | reports/services/sales_summary.py: DailySalesSummaryService | ⚠️ EXISTS | P1 | Verify completeness |

**Action for 3a:** Create finance/services.py with:
```python
def auto_generate_obligations():
    # Idempotent: check ObligationGeneratorLog
    # Generate for current + next 2 months
    # Use RecurrencePattern.next_due_date()
```

**Action for 3b:** Create reports/periods.py with:
```python
class ReportPeriod:
    start: date
    end: date
    preset: str
    reference: str
    
    @classmethod
    def resolve(cls, preset, start, end, default_preset='this_month')
    
PRESET_CHOICES = [
    ('today', 'Today'),
    ('yesterday', 'Yesterday'),
    ('this_week', 'This Week'),
    ('last_week', 'Last Week'),
    ('this_month', 'This Month'),
    ('last_month', 'Last Month'),
    ('this_quarter', 'This Quarter'),
    ('last_quarter', 'Last Quarter'),
    ('this_year', 'This Year'),
    ('last_year', 'Last Year'),
]
```

---

### PHASE 4 — Forms

| # | Task | Status | Priority | File |
|---|------|--------|----------|------|
| 4a | reports/forms.py: ReportPeriodForm | ❌ TODO | P0 | preset + start/end fields |
| 4b | finance/forms.py: ExpenseItemForm | ❌ TODO | P0 | All fields + widget attrs |
| 4c | finance/forms.py: ExpenseRateForm | ❌ TODO | P1 | rate + effective_date |
| 4d | finance/forms.py: PaymentForm | ❌ TODO | P0 | obligation FK, amount, method, date |
| 4e | finance/forms.py: LiabilityPaymentForm | ❌ TODO | P1 | principal + interest split |
| 4f | assets/forms.py: AssetForm | ❌ TODO | P0 | All fields including depreciation |
| 4g | sales/forms.py: SaleForm (upgrade) | ❌ TODO | P0 | HTMX live search, auto-fill price |
| 4h | credit/forms.py: DebtReturnForm (upgrade) | ❌ TODO | P0 | Filter debts by debtor, pre-fill balance |

**Action for 4a:** Create reports/forms.py:
```python
class ReportPeriodForm(forms.Form):
    preset = forms.ChoiceField(choices=PRESET_CHOICES)
    start = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    def resolved_period(self, default_preset='this_month'):
        # Return ReportPeriod instance
```

**Action for 4g:** Upgrade sales/forms.py SaleForm:
- product_spec field: use ModelSelect2 widget OR plain text input with HTMX autocomplete
- On product_spec change: HTMX request to fetch default_selling_price
- Show current stock badge next to quantity field
- Clean: validate qty <= current_stock

---

### PHASE 5 — Report Views Implementation

| # | View | Status | Priority | Service Used |
|---|------|--------|----------|--------------|
| 5a | reports/views/index.py | ⚠️ EXISTS | P2 | Static links only |
| 5b | reports/views/income_statement.py | ⚠️ EXISTS | P0 | AccountingService + ExpenseService |
| 5c | reports/views/balance_sheet.py | ⚠️ EXISTS | P0 | BalanceSheetService |
| 5d | reports/views/cash_flow.py | ⚠️ EXISTS | P1 | CashFlowService |
| 5e | reports/views/debtor_aging.py | ⚠️ EXISTS | P0 | Inline aging logic |
| 5f | reports/views/daily_sales.py | ⚠️ EXISTS | P1 | DailySalesSummaryService |
| 5g | reports/views/stock_report.py | ⚠️ EXISTS | P1 | ProductSpec queryset |
| 5h | reports/views/expense_analysis.py | ⚠️ EXISTS | P1 | ExpenseService |
| 5i | reports/views/liability_schedule.py | ⚠️ EXISTS | P1 | LiabilityItem queries |
| 5j | reports/views/drawings_summary.py | ⚠️ EXISTS | P2 | Drawing queryset |
| 5k | reports/views/purchase_summary.py | ⚠️ EXISTS | P2 | Purchase + PurchaseDetail |
| 5l | reports/views/product_profitability.py | ⚠️ EXISTS | P1 | ProductSpec + ExpressionWrapper |
| 5m | reports/views/budget_vs_actual.py | ⚠️ EXISTS | P2 | BudgetLine (if exists) |
| 5n | reports/views/low_stock.py | ⚠️ EXISTS | P1 | ProductSpec filtered |
| 5o | reports/views/cash_reconciliation.py | ⚠️ EXISTS | P1 | CashRegisterSession |
| 5p | reports/views/snapshots.py | ⚠️ EXISTS | P2 | ReportSnapshot |
| 5q | reports/urls.py: wire all 16 views | ❌ TODO | P0 | URL patterns |
| 5r | BaseReportView: implement get/post, PDF export | ⚠️ EXISTS | P0 | reports/views/base.py |

**Action for each view file:**
```python
from reports.views.base import BaseReportView
from reports.services.accounting import AccountingService
from reports.services.expenses import ExpenseService

class IncomeStatementView(BaseReportView):
    report_code = 'PnL'
    template_name = 'reports/income_statement.html'
    
    def get_context_data(self, period, **kwargs):
        accounting = AccountingService(period.start, period.end)
        expenses = ExpenseService(period.start, period.end)
        return {
            'period': period,
            'revenue': accounting.net_sales(),
            'cogs': accounting.cogs(),
            'gross_profit': accounting.gross_profit(),
            'expenses_by_type': expenses.by_type(),
            'net_profit': accounting.net_profit(),
        }
```

**Action for 5q:** Create reports/urls.py:
```python
from django.urls import path
from .views import income_statement, balance_sheet, cash_flow, ...

app_name = 'reports'
urlpatterns = [
    path('', income_statement.index, name='index'),
    path('income-statement/', income_statement.IncomeStatementView.as_view(), name='income-statement'),
    path('balance-sheet/', balance_sheet.BalanceSheetView.as_view(), name='balance-sheet'),
    # ... 14 more
]
```

---

### PHASE 6 — Finance Views (Full CRUD + HTMX)

| # | View | URL | Method | Status | Priority |
|---|------|-----|--------|--------|----------|
| 6a | Finance Index | /finance/ | GET | ⚠️ EXISTS | P0 |
| 6b | ExpenseItem List | /finance/expenses/ | GET | ❌ TODO | P0 |
| 6c | ExpenseItem Create | /finance/expenses/new/ | GET/POST | ❌ TODO | P0 |
| 6d | ExpenseItem Detail | /finance/expenses/<pk>/ | GET | ❌ TODO | P0 |
| 6e | ExpenseRate Create | /finance/expenses/<pk>/rate/ | GET/POST | ❌ TODO | P1 |
| 6f | ExpenseItem Toggle | /finance/expenses/<pk>/toggle/ | POST | ❌ TODO | P1 |
| 6g | Obligation Pay (HTMX) | /finance/obligation/<pk>/pay/ | GET/POST | ❌ TODO | P0 |
| 6h | Liability List | /finance/liabilities/ | GET | ❌ TODO | P1 |
| 6i | Liability Detail | /finance/liabilities/<pk>/ | GET | ❌ TODO | P1 |
| 6j | Liability Pay (HTMX) | /finance/liabilities/<pk>/pay/ | GET/POST | ❌ TODO | P1 |
| 6k | Prepayment List | /finance/prepayments/ | GET | ❌ TODO | P2 |
| 6l | Prepayment Create | /finance/prepayments/new/ | GET/POST | ❌ TODO | P2 |

**Action for 6a (Index upgrade):**
```python
def index(request):
    auto_generate_obligations()  # Idempotent
    overdue = PaymentObligation.objects.overdue()
    due_this_month = PaymentObligation.objects.due_this_month()
    upcoming = PaymentObligation.objects.upcoming()
    return render(request, 'finance/index.html', {
        'overdue': overdue,
        'due_this_month': due_this_month,
        'upcoming': upcoming,
    })
```

**Action for 6g (HTMX endpoint):**
```python
def obligation_pay(request, pk):
    obligation = get_object_or_404(PaymentObligation, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.obligation = obligation
            payment.save()
            obligation.amount_paid += payment.amount
            obligation.save()
            return render(request, 'finance/_obligation_row.html', {'obligation': obligation})
    else:
        form = PaymentForm(initial={'amount': obligation.balance, 'obligation': obligation})
        return render(request, 'finance/_obligation_pay_form.html', {'form': form, 'obligation': obligation})
```

---

### PHASE 7 — Assets Views

| # | View | URL | Status | Priority |
|---|------|-----|--------|----------|
| 7a | Asset Index | /assets/ | ⚠️ EXISTS | P1 |
| 7b | Asset Detail | /assets/<pk>/ | ❌ TODO | P0 |
| 7c | Asset Create | /assets/new/ | ❌ TODO | P1 |
| 7d | Asset Edit | /assets/<pk>/edit/ | ❌ TODO | P1 |
| 7e | Asset Disposal | /assets/<pk>/dispose/ | ❌ TODO | P1 |
| 7f | Depreciation Schedule (partial) | /assets/<pk>/depreciation/ | ❌ TODO | P2 |

**Action for 7b (Detail):**
```python
class AssetDetailView(DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        asset = self.object
        ctx['accumulated_depreciation'] = asset.accumulated_depreciation
        ctx['net_book_value'] = asset.net_book_value
        ctx['depreciation_schedule'] = asset.depreciation_schedule()[:12]  # Next 12 months
        return ctx
```

---

### PHASE 8 — Self-Sufficient View Upgrades

#### 8.1 Catalog App

| # | View | Current | Required | Priority |
|---|------|---------|----------|----------|
| 8a | ProductSpec Detail | Shows basic info | Add: inline sell/purchase/credit sale/office use/drawing buttons (HTMX) | P0 |
| 8b | Product Detail | Shows product info | Add: all specs table, recent sales/purchases, action buttons | P0 |
| 8c | HTMX Endpoint: Sell | N/A | /catalog/products/<pk>/sell/ → returns sale form partial | P0 |
| 8d | HTMX Endpoint: Purchase | N/A | /catalog/products/<pk>/purchase/ → returns purchase form partial | P0 |
| 8e | HTMX Endpoint: Credit Sale | N/A | /catalog/products/<pk>/credit-sale/ → returns debt form partial | P0 |
| 8f | HTMX Endpoint: Office Use | N/A | /catalog/products/<pk>/office-use/ → returns office use form partial | P1 |
| 8g | HTMX Endpoint: Drawing | N/A | /catalog/products/<pk>/drawing/ → returns drawing form partial | P1 |

#### 8.2 Sales App

| # | View | Current | Required | Priority |
|---|------|---------|----------|----------|
| 8h | Sale List | Basic list | Add: today's total, payment method breakdown, [New Sale] HTMX slide-in | P0 |
| 8i | Sale Detail | Basic detail | Add: [Return] button, linked product, payment method | P1 |
| 8j | HTMX Endpoint: New Sale | N/A | /sales/new-htmx/ → returns sale form partial (slide-in panel) | P0 |
| 8k | HTMX Endpoint: Return | N/A | /sales/<pk>/return/ → returns return inward form partial | P0 |

#### 8.3 Credit App

| # | View | Current | Required | Priority |
|---|------|---------|----------|----------|
| 8l | Debtor List | Basic list | Add: outstanding balance per debtor, total receivables, [Quick Repayment] per row | P0 |
| 8m | Debtor Detail | Basic detail | Add: all debts with balances, all repayments, [Record Repayment] per debt, [Block/Unblock] toggle | P0 |
| 8n | HTMX Endpoint: Repayment | N/A | /credit/debtors/<pk>/repay/ → returns repayment form partial | P0 |
| 8o | HTMX Endpoint: Block | N/A | /credit/debtors/<pk>/toggle-block/ → POST, returns updated row | P1 |

#### 8.4 Inventory App

| # | View | Current | Required | Priority |
|---|------|---------|----------|----------|
| 8p | Purchase Detail | Basic detail | Add: all line items table, [Add Line Item] inline form, [Return Item] per line | P0 |
| 8q | HTMX Endpoint: Add Line | N/A | /inventory/purchases/<pk>/add-line/ → returns purchase detail form partial | P0 |
| 8r | HTMX Endpoint: Return Outward | N/A | /inventory/purchases/<pk>/return/ → returns return outward form partial | P0 |

#### 8.5 Dashboard

| # | Widget | Current | Required | Priority |
|---|--------|---------|----------|----------|
| 8s | Revenue Cards | May exist | Today/MTD/YTD revenue, clickable to filtered sales report | P0 |
| 8t | Receivables Widget | May exist | Outstanding total, overdue count, link to credit app | P0 |
| 8u | Stock Widget | May exist | Low stock count, out of stock count, link to low stock report | P0 |
| 8v | Obligations Widget | May exist | Overdue obligations count, link to finance filtered | P0 |
| 8w | Recent Sales | May exist | Last 10 sales, links to detail | P1 |
| 8x | Top Products | N/A | Top 5 products today by qty/revenue | P1 |
| 8y | [New Sale] Button | N/A | HTMX slide-in panel (same as sales list) | P0 |

---

### PHASE 9 — Template Implementation

**All templates must:**
- `{% extends "base.html" %}`
- `{% load humanize %}` (after adding to INSTALLED_APPS)
- Use Tailwind CSS classes
- Format TZS: `|floatformat:0|intcomma`
- Include HTMX attributes for inline actions
- Have NO placeholders like "TODO" or "Coming soon"

| # | Template | App | Status | Priority | Key Features |
|---|----------|-----|--------|----------|--------------|
| 9a | base.html | global | ✅ EXISTS | - | Has HTMX script, sidebar |
| 9b | dashboard/index.html | dashboard | ⚠️ EXISTS | P0 | Revenue cards, widgets, [New Sale] |
| 9c | catalog/product_detail.html | catalog | ❓ CHECK | P0 | Specs table, recent activity, 5 action buttons |
| 9d | catalog/product_list.html | catalog | ❓ CHECK | P1 | Search, filter, links to detail |
| 9e | sales/sale_list.html | sales | ❓ CHECK | P0 | Date filter, totals, [New Sale] slide-in, [Return] per row |
| 9f | sales/sale_detail.html | sales | ❓ CHECK | P1 | Linked product, payment method, [Return] button |
| 9g | sales/_sale_form_partial.html | sales | ❌ TODO | P0 | HTMX partial for slide-in |
| 9h | credit/index.html (debtor list) | credit | ❓ CHECK | P0 | Outstanding balances, [Quick Repayment] per row |
| 9i | credit/debtor_detail.html | credit | ❓ CHECK | P0 | All debts, all repayments, [Repay] per debt, [Block] toggle |
| 9j | credit/_repayment_form_partial.html | credit | ❌ TODO | P0 | HTMX partial |
| 9k | inventory/index.html | inventory | ❓ CHECK | P1 | Purchases list, suppliers |
| 9l | inventory/purchase_detail.html | inventory | ❓ CHECK | P0 | Line items table, [Add Line], [Return] per line |
| 9m | inventory/_purchase_line_form.html | inventory | ❌ TODO | P0 | HTMX inline form |
| 9n | finance/index.html | finance | ❓ CHECK | P0 | Overdue (red), due this month (amber), upcoming (green), [Pay] per obligation |
| 9o | finance/expense_list.html | finance | ❌ TODO | P0 | Searchable, filterable |
| 9p | finance/expense_detail.html | finance | ❌ TODO | P0 | Obligations grouped, payments, [Pay Latest], [Change Rate], [Toggle] |
| 9q | finance/_obligation_pay_form.html | finance | ❌ TODO | P0 | HTMX partial |
| 9r | finance/liability_list.html | finance | ❌ TODO | P1 | Balances, next payment due |
| 9s | finance/liability_detail.html | finance | ❌ TODO | P1 | Amortisation schedule, payment history, [Pay] |
| 9t | assets/index.html | assets | ❓ CHECK | P1 | Grouped by category, totals |
| 9u | assets/asset_detail.html | assets | ❌ TODO | P0 | Depreciation schedule, NBV, [Edit], [Dispose] |
| 9v | reports/index.html | reports | ❓ CHECK | P2 | Quick links to all reports |
| 9w | reports/income_statement.html | reports | ❓ CHECK | P0 | Period form, P&L table, PDF button |
| 9x | reports/balance_sheet.html | reports | ❓ CHECK | P0 | Period form, balance sheet table, equation check |
| 9y | reports/cash_flow.html | reports | ❓ CHECK | P1 | Indirect method table |
| 9z | reports/debtor_aging.html | reports | ❓ CHECK | P0 | Aging buckets, totals |
| 9aa | reports/daily_sales.html | reports | ❓ CHECK | P1 | By payment method, by transaction type, top products |
| 9ab | reports/stock_report.html | reports | ❓ CHECK | P1 | All specs with stock, WAC, value |
| 9ac | reports/expense_analysis.html | reports | ❓ CHECK | P1 | By type, by item, obligations summary |
| 9ad | reports/liability_schedule.html | reports | ❓ CHECK | P1 | All liabilities, schedules |
| 9ae | reports/drawings_summary.html | reports | ❓ CHECK | P2 | Total drawings by type |
| 9af | reports/purchase_summary.html | reports | ❓ CHECK | P2 | By supplier, by product |
| 9ag | reports/product_profitability.html | reports | ❓ CHECK | P1 | Margin per product |
| 9ah | reports/budget_vs_actual.html | reports | ❓ CHECK | P2 | Variance analysis |
| 9ai | reports/low_stock.html | reports | ❓ CHECK | P1 | Filtered list, reorder alerts |
| 9aj | reports/cash_reconciliation.html | reports | ❓ CHECK | P1 | Session balances, uncleared cheques |
| 9ak | reports/snapshots.html | reports | ❓ CHECK | P2 | Historical reports list |
| 9al | _modal.html | global | ❌ TODO | P0 | Reusable HTMX modal component |
| 9am | _slide_in_panel.html | global | ❌ TODO | P0 | Reusable slide-in panel for forms |
| 9an | _nudge_buttons.html | global | ❌ TODO | P1 | Nudge.js integration for messages |

**Action for modal component (9al):**
```html
<!-- templates/_modal.html -->
<div id="htmx-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden z-50 flex items-center justify-center"
     onclick="if(event.target === this) this.classList.add('hidden')">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4"
         onclick="event.stopPropagation()">
        <div class="p-4 border-b flex justify-between items-center">
            <h3 class="text-lg font-semibold" id="modal-title">{% block modal_title %}{% endblock %}</h3>
            <button onclick="document.getElementById('htmx-modal').classList.add('hidden')" 
                    class="text-gray-500 hover:text-gray-700">&times;</button>
        </div>
        <div class="p-4" id="modal-content">
            {% block modal_content %}{% endblock %}
        </div>
    </div>
</div>
```

---

### PHASE 10 — Integrity + Testing

| # | Task | Status | Priority |
|---|------|--------|----------|
| 10a | Test accounting equation: Opening + Net Purchases = COGS + Closing | ❌ TODO | P0 |
| 10b | Test WAC calculation matches manual calc for 3 products | ❌ TODO | P0 |
| 10c | Test all 7 transaction types affect stock correctly | ❌ TODO | P0 |
| 10d | Test debtor blocking prevents new credit sales | ❌ TODO | P1 |
| 10e | Test obligation generation is idempotent | ❌ TODO | P1 |
| 10f | Test balance sheet balances (Assets = Liabilities + Equity) | ❌ TODO | P0 |
| 10g | Load test: 100 concurrent users, measure response time | ❌ TODO | P2 |
| 10h | Security: verify CSRF on all POST endpoints | ❌ TODO | P1 |
| 10i | Accessibility: tab navigation works on all forms | ❌ TODO | P2 |

---

## CRITICAL PATH (MVP for Demo)

1. **P0 Tasks Only** (can demo after these):
   - 1b: Add humanize to INSTALLED_APPS
   - 1d: Make models inherit TimestampedModel (at least core ones)
   - 2a-2b: ProductSpec cached_wac + refresh_wac()
   - 2m-2n: Migrations + backfill WAC
   - 3a: auto_generate_obligations()
   - 3b: ReportPeriod class
   - 4a: ReportPeriodForm
   - 5b-5f, 5q-5r: Core report views (P&L, Balance Sheet, Cash Flow, Debtor Aging, Daily Sales) + URLs
   - 6a, 6b-6g: Finance index + expense CRUD + obligation pay HTMX
   - 7b: Asset detail
   - 8a-8g: Product spec inline actions
   - 8h-8k: Sales list with [New Sale] + [Return]
   - 8l-8o: Debtor list/detail with [Repayment]
   - 9b-9s, 9w-9ad: All corresponding templates
   - 9al-9am: Modal + slide-in components
   - 10a-10c, 10f: Accounting integrity tests

2. **After MVP** (P1/P2 tasks):
   - Remaining reports
   - Budget vs Actual
   - Snapshots
   - Load testing
   - Accessibility

---

## ESTIMATED EFFORT

| Phase | P0 Tasks | P1 Tasks | P2 Tasks | Total |
|-------|----------|----------|----------|-------|
| Phase 1 | 2 | 0 | 0 | 2 |
| Phase 2 | 6 | 6 | 0 | 12 |
| Phase 3 | 2 | 2 | 0 | 4 |
| Phase 4 | 4 | 4 | 0 | 8 |
| Phase 5 | 8 | 6 | 2 | 16 |
| Phase 6 | 6 | 4 | 2 | 12 |
| Phase 7 | 1 | 4 | 1 | 6 |
| Phase 8 | 15 | 8 | 4 | 27 |
| Phase 9 | 20 | 10 | 5 | 35 |
| Phase 10 | 4 | 3 | 2 | 9 |
| **TOTAL** | **68** | **47** | **16** | **131** |

**Rough Time Estimate:**
- P0 (68 tasks): ~40-50 hours (critical path)
- P1 (47 tasks): ~30-40 hours (polish)
- P2 (16 tasks): ~10-15 hours (nice-to-have)
- **Total: ~80-105 hours**

---

## NEXT IMMEDIATE ACTIONS

1. Add `django.contrib.humanize` to `kiyabo_duka/settings.py` INSTALLED_APPS
2. Update ALL models to inherit from `apps.core.models.TimestampedModel`
3. Add `cached_wac`, `cached_stock_value` to ProductSpec + `refresh_wac()` method
4. Create `finance/services.py` with `auto_generate_obligations()`
5. Create `reports/periods.py` with `ReportPeriod` class
6. Create `reports/forms.py` with `ReportPeriodForm`
7. Implement core report views (Income Statement, Balance Sheet, Cash Flow)
8. Wire up reports/urls.py
9. Upgrade finance/views.py with CRUD + HTMX endpoints
10. Build self-sufficient templates with inline actions

---

## FILES REQUIRING MAJOR WORK

| File | Current State | Required State | Effort |
|------|---------------|----------------|--------|
| kiyabo_duka/settings.py | Missing humanize | Add humanize | 5 min |
| catalog/models.py | No TimestampedModel | Inherit TimestampedModel, add cached_wac | 1 hour |
| finance/services.py | MISSING | auto_generate_obligations() | 2 hours |
| reports/periods.py | MISSING | ReportPeriod class + presets | 1 hour |
| reports/forms.py | MISSING | ReportPeriodForm | 30 min |
| finance/forms.py | MISSING | 4 forms | 2 hours |
| assets/forms.py | MISSING | AssetForm | 1 hour |
| sales/forms.py | Basic | HTMX live search, auto-fill | 2 hours |
| credit/forms.py | Basic | Debt filtering, pre-fill | 1 hour |
| reports/views/*.py | Stubs | Full implementations | 8 hours |
| finance/views.py | Index only | Full CRUD + HTMX | 4 hours |
| assets/views.py | Index only | Detail + disposal | 2 hours |
| catalog/views.py | Basic | Inline action endpoints | 3 hours |
| sales/views.py | Basic | HTMX endpoints | 2 hours |
| credit/views.py | Basic | HTMX endpoints | 2 hours |
| templates/**/*.html | 70 files, no HTMX | All with inline actions | 15 hours |

---

## SUCCESS CRITERIA

A page is "self-sufficient" when:
1. ✅ Shows ALL related data (no need to navigate elsewhere to see context)
2. ✅ Provides inline actions for EVERY possible operation from that context
3. ✅ Uses HTMX for all actions (no full page reloads)
4. ✅ Pre-fills forms with contextual data (product, debtor, etc.)
5. ✅ Shows validation feedback inline (Nudge.js or similar)
6. ✅ Updates the UI immediately after action (no manual refresh)

**Example: Product Detail Page**
- Shows: product info, all specs with stock/WAC/value, recent sales/purchases
- Actions: [Sell], [Purchase], [Credit Sale], [Office Use], [Drawing] — all open HTMX modals pre-filled with this product
- After selling: stock updates immediately, recent sales list refreshes, no page reload

---

## NOTES

- **DO NOT** use Sum('amount') for COGS — use ExpressionWrapper(F('qty') * F('unit_cost'))
- **DO NOT** filter PaymentMethod by name — always use category.code
- **DO** make all service methods idempotent where possible
- **DO** use HTMX for all inline actions (modals, slide-ins, inline forms)
- **DO** pre-fill every form with maximum contextual data
- **DO** show stock levels, balances, and limits prominently
- **DO** validate on both client and server side
- **DO** log all destructive actions (deletions, disposals, write-offs)

---

*This document is a living checklist. Update status columns as work progresses.*
