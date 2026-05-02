# Kiyabo Duka — Django Migration Master Plan
## From MS Access v0.031 → Production-Grade Django + PostgreSQL

**Shop:** Upendo Stationery (operated via Kiyabo Duka system)  
**Location:** Dar es Salaam, Tanzania  
**Currency:** TZS (Tanzanian Shillings)  
**Timezone:** Africa/Dar_es_Salaam  
**Source system:** MS Access v0.031 — 33 tables, 44 relationships, 4,020+ sales records  
**Target stack:** Django 5.x · PostgreSQL 16 · WeasyPrint · Celery (optional) · Bootstrap 5  
**Document version:** 1.0 — May 2026  
**Status:** Living reference — update as decisions are made

---

## Table of Contents

1. [Business Understanding — What Kiyabo Duka Actually Does](#1-business-understanding)
2. [Accounting Engine — The Brain of the System](#2-accounting-engine)
3. [Data Model — All 33 Tables Mapped to Django](#3-data-model)
4. [Django App Architecture](#4-django-app-architecture)
5. [Models — Full Django ORM Code](#5-models)
6. [Services Layer — VBA Business Logic in Python](#6-services-layer)
7. [Forms & Views — Every Screen Mapped](#7-forms-and-views)
8. [Reports — Accounting-Grade Output](#8-reports)
9. [Admin Configuration](#9-admin-configuration)
10. [URL Structure](#10-url-structure)
11. [Project Setup & Settings](#11-project-setup)
12. [Data Migration Checklist](#12-data-migration-checklist)
13. [Testing Strategy](#13-testing-strategy)
14. [Deployment](#14-deployment)

---

## 1. Business Understanding

### What This Shop Sells

Upendo Stationery is a retail stationery shop. Products span 14 categories, 51 types, 18 brands, 90 product specs, and 123 named products. Every product has a **spec dimension** (e.g., size, colour, variant) so the same notebook can be sold in A4 or A5 — each is a distinct `ProductSpec`. There are 9 spec dimensions (specs) with 44 values (spec_values).

### The Seven Transaction Types

This is the most critical thing to understand before building a single view. The system tracks **seven distinct inventory movement types**, each with different effects on the Income Statement and Balance Sheet:

| # | Transaction | Table | Stock Effect | Revenue Effect | Notes |
|---|---|---|---|---|---|
| 1 | **Direct Sale** | `tbl_sales` | ↓ Decreases | ↑ Increases Net Sales | Cash or M-Pesa at counter |
| 2 | **Credit Sale** | `tbl_debts` | ↓ Decreases | ↑ Increases Net Sales | Creates Accounts Receivable |
| 3 | **Return Inward** | `tbl_return_inwards` | ↑ Increases | ↓ Reduces Net Sales | Customer returns defective item |
| 4 | **Purchase** | `tbl_purchase_details` | ↑ Increases | — | Stock replenishment |
| 5 | **Return Outward** | `tbl_return_outwards` | ↓ Decreases | — | Returns to supplier |
| 6 | **Office Use** | `tbl_sales_office_use` | ↓ Decreases | — | Internal consumption, expensed |
| 7 | **Drawing** | `tbl_drawings` | ↓ Decreases | — | Owner withdrawal, reduces equity |

**The validation equation (must always hold):**
```
Opening Stock + Net Purchases = COGS + Closing Stock
```
This is the core accounting integrity check. Django services must enforce this.

### Stock Calculation Formula

```python
current_stock = (
    purchased_qty
    + return_inwards_qty          # goods coming back in
    - sold_qty                    # direct cash sales
    - credit_sales_qty            # credit sales (also leaves stock)
    - return_outwards_qty         # sent back to supplier
    - office_use_qty              # consumed internally
    - drawings_qty                # taken by owner
)
```

This is computed by `modStockCRUD.UpdateProductsStock()` in VBA. In Django it becomes a database function or a service method called after every transaction.

### Costing Method: Weighted Average (GAAP Compliant)

The system uses **Weighted Average Costing** for COGS, not FIFO or LIFO. The weighted average cost per unit changes with every purchase batch. This is implemented in `modAccountings` and must be replicated exactly:

```
Weighted Average Cost = Total Cost of All Purchases / Total Units Purchased
COGS = Weighted Avg Cost × Total Units Outflowed (sold + credit + office use + drawings)
```

### Financial Periods

The system tracks `month_id` and `month_name` on every transaction table. This is used for period-based reporting. In Django, these denormalized fields **should NOT be stored** — derive them from `sale_date` using Django's `TruncMonth` and `ExtractMonth` database functions.

### The Expense Engine

Expenses are **not simple flat entries**. The system has a multi-level structure:

```
ExpenseType (e.g., "Rent", "Salaries")
    └── ExpenseItem (e.g., "Shop Rent — Kariakoo Branch")
           ├── ExpenseRate (historical rates, effective_from date — handles rate changes)
           ├── RecurrencePattern (Monthly/Weekly, specific day, start/end date)
           └── PaymentObligation (auto-generated due date entries)
                   ├── Payment (actual cash outflow)
                   └── Prepayment (advance payments applied against obligations)
```

`modPayables.GenerateObligations()` auto-generates `PaymentObligation` rows from recurrence patterns. This must be a Django management command or Celery periodic task.

### Liabilities

The system tracks external borrowings:

```
LiabilityCategory → LiabilityType → LiabilityItem
                                         └── LiabilityPaymentDetail (principal + interest breakdown)
```

Each liability has `rate` (interest rate), `amount_per_return`, `maturity_date`. Payments split into principal and interest components.

### Credit Sales & Debtor Management

Credit sales create `tbl_debts` records (NOT to be confused with external loans). Each debt:
- Links to a `Debtor` (customer with NIDA ID, phone, address)
- Has `expected_payment_date`
- Is repaid via `tbl_debt_returns` (multiple partial payments allowed)
- Tracks `payment_method_id` for each repayment

The P&L sample shows: `Credit Sales: 0.00` and `Direct Sales: 18,900.00` — both contribute to `Net Sales`.

### Assets Register

Simple fixed asset tracking: `AssetCategory → AssetType → Asset` with `asset_worth` and `date_checked`.

---

## 2. Accounting Engine

### Income Statement Structure (from live P&L)

```
INCOME STATEMENT — [Period Start] to [Period End]

REVENUE
  Direct Sales                               18,900.00
  Credit Sales                                    0.00
  Less: Return Inwards                            0.00
                                           ──────────
  NET SALES                                  18,900.00

COST OF GOODS SOLD
  Opening Stock                           3,026,350.00
  Add: Purchases                                  0.00
  Add: Carriage Inwards                           0.00
  Less: Return Outwards                           0.00
                                           ──────────
  Net Purchases                                   0.00
  Cost of Goods Available for Sale (COGAS)  3,026,350.00
  Less: Closing Stock                      3,011,400.00
                                           ──────────
  COST OF GOODS SOLD (COGS)                  14,950.00

GROSS PROFIT                                 3,750.00

OPERATING EXPENSES
  Office Use / Customer Care                    200.00
  Kodi (Rent)                                     0.00
  Mshahara (Salaries)                             0.00
  Umeme (Electricity)                             0.00
  Matangazo (Advertising)                         0.00
  Matengenezo (Maintenance)                       0.00
  Usafi (Cleaning)                                0.00
                                           ──────────
  TOTAL OPERATING EXPENSES                       200.00  [note: shown as 0 in sample]

NET PROFIT                                    3,750.00
```

**Key accounting observations:**
- COGS includes **all inventory outflows** at weighted average cost (sales, credit sales, office use, drawings)
- Office Use reduces gross profit (it's COGS) AND is listed as an expense — this double-counts unless the Office Use items are excluded from COGS. The VBA comments in `modAccountings` clarify: Office Use IS included in COGS (cost of goods consumed). Whether it also appears in expenses is a presentation choice to clarify what left inventory for non-sale reasons.
- The validation equation must hold: `3,026,350 + 0 = 14,950 + 3,011,400 = 3,026,350` ✓

### Python Accounting Service

```python
# apps/reports/services/accounting.py

from decimal import Decimal
from datetime import date
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import Coalesce

class AccountingService:
    """
    Weighted Average Cost inventory accounting engine.
    Mirrors modAccountings VBA logic 1:1.
    All monetary values in TZS (stored as Decimal).
    """

    def __init__(self, start_date: date, end_date: date, product_spec_id: int = None):
        self.start = start_date
        self.end = end_date
        self.spec_id = product_spec_id  # None = aggregate all products

    # ── QUANTITY FUNCTIONS ──────────────────────────────────────────────────

    def _qty(self, qs, field='quantity'):
        return qs.aggregate(total=Coalesce(Sum(field), Decimal('0')))['total']

    def purchased_qty(self):
        from apps.inventory.models import PurchaseDetail
        qs = PurchaseDetail.objects.filter(
            purchase__purchase_date__date__range=(self.start, self.end)
        )
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def sold_qty(self):
        from apps.sales.models import Sale
        qs = Sale.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def credit_sales_qty(self):
        from apps.credit.models import Debt
        qs = Debt.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def return_inwards_qty(self):
        from apps.sales.models import ReturnInward
        qs = ReturnInward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(sale__product_spec_id=self.spec_id)
        return self._qty(qs)

    def return_outwards_qty(self):
        from apps.inventory.models import ReturnOutward
        qs = ReturnOutward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(purchase_detail__product_spec_id=self.spec_id)
        return self._qty(qs)

    def office_use_qty(self):
        from apps.sales.models import SaleOfficeUse
        qs = SaleOfficeUse.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def drawings_qty(self):
        from apps.sales.models import Drawing
        qs = Drawing.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    # ── MONETARY FUNCTIONS ──────────────────────────────────────────────────

    def _val(self, qs, field='amount'):
        return qs.aggregate(total=Coalesce(Sum(field), Decimal('0')))['total']

    def direct_sales(self):
        from apps.sales.models import Sale
        qs = Sale.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._val(qs)

    def credit_sales(self):
        from apps.credit.models import Debt
        qs = Debt.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._val(qs)

    def net_sales(self):
        return self.direct_sales() + self.credit_sales() - self.return_inwards()

    def purchases(self):
        from apps.inventory.models import PurchaseDetail
        qs = PurchaseDetail.objects.filter(
            purchase__purchase_date__date__range=(self.start, self.end)
        )
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._val(qs, 'amount')

    def return_inwards(self):
        from apps.sales.models import ReturnInward
        qs = ReturnInward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(sale__product_spec_id=self.spec_id)
        return self._val(qs)

    def return_outwards(self):
        from apps.inventory.models import ReturnOutward
        qs = ReturnOutward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(purchase_detail__product_spec_id=self.spec_id)
        return self._val(qs)

    def net_purchases(self):
        return self.purchases() - self.return_outwards()

    def weighted_average_cost(self) -> Decimal:
        """
        Compute weighted average cost per unit for the product spec.
        Only meaningful when spec_id is set.
        Formula: total_purchase_cost / total_purchased_qty
        """
        from apps.inventory.models import PurchaseDetail
        qs = PurchaseDetail.objects.all()
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        total_cost = self._val(qs, 'amount')
        total_qty = self._qty(qs)
        if total_qty == 0:
            return Decimal('0')
        return total_cost / total_qty

    def opening_stock_value(self) -> Decimal:
        """
        Opening stock = units in stock at start of period × weighted avg cost as of period start.
        """
        # Use a service scoped to upToDate = self.start - 1 day
        from datetime import timedelta
        prior_end = self.start - timedelta(days=1)
        prior_svc = AccountingService(date(2000, 1, 1), prior_end, self.spec_id)
        opening_qty = prior_svc._closing_stock_qty()
        wac = prior_svc.weighted_average_cost()
        return opening_qty * wac

    def _closing_stock_qty(self) -> Decimal:
        return (
            self.purchased_qty()
            + self.return_inwards_qty()
            - self.sold_qty()
            - self.credit_sales_qty()
            - self.return_outwards_qty()
            - self.office_use_qty()
            - self.drawings_qty()
        )

    def closing_stock_value(self) -> Decimal:
        closing_qty = self._closing_stock_qty()
        wac = self.weighted_average_cost()
        return closing_qty * wac

    def cogs(self) -> Decimal:
        """
        COGS = Opening Stock + Net Purchases - Closing Stock
        VALIDATION: opening + net_purchases == cogs + closing (must hold)
        """
        opening = self.opening_stock_value()
        net_purch = self.net_purchases()
        closing = self.closing_stock_value()
        return opening + net_purch - closing

    def gross_profit(self) -> Decimal:
        return self.net_sales() - self.cogs()

    def to_income_statement(self) -> dict:
        """Returns full income statement data dict for template rendering."""
        direct = self.direct_sales()
        credit = self.credit_sales()
        ret_in = self.return_inwards()
        net_sales = direct + credit - ret_in

        purch = self.purchases()
        ret_out = self.return_outwards()
        net_purch = purch - ret_out
        opening = self.opening_stock_value()
        cogas = opening + net_purch
        closing = self.closing_stock_value()
        cogs = cogas - closing
        gross_profit = net_sales - cogs

        return {
            'period_start': self.start,
            'period_end': self.end,
            'direct_sales': direct,
            'credit_sales': credit,
            'return_inwards': ret_in,
            'net_sales': net_sales,
            'opening_stock': opening,
            'purchases': purch,
            'carriage_inwards': Decimal('0'),  # not tracked yet
            'return_outwards': ret_out,
            'net_purchases': net_purch,
            'cogas': cogas,
            'closing_stock': closing,
            'cogs': cogs,
            'gross_profit': gross_profit,
            # Operating expenses supplied by ExpenseService
        }
```

---

## 3. Data Model

### Complete Table → Django Model Mapping (All 33 Tables)

| Access Table | Django App | Django Model | Records |
|---|---|---|---|
| tbl_categories | catalog | Category | 14 |
| tbl_types | catalog | ProductType | 51 |
| tbl_brands | catalog | Brand | 18 |
| tbl_units | catalog | Unit | — |
| tbl_specs | catalog | Spec | 9 |
| tbl_spec_values | catalog | SpecValue | 44 |
| tbl_products | catalog | Product | 123 |
| tbl_product_specs | catalog | ProductSpec | 90 |
| tbl_suppliers | inventory | Supplier | 4 |
| tbl_purchases | inventory | Purchase | 74 |
| tbl_purchase_details | inventory | PurchaseDetail | 357 |
| tbl_return_outwards | inventory | ReturnOutward | 6 |
| tbl_sales | sales | Sale | 4,020 |
| tbl_return_inwards | sales | ReturnInward | 0 |
| tbl_sales_office_use | sales | SaleOfficeUse | 2 |
| tbl_office_use | sales | OfficeUseCategory | 6 |
| tbl_drawings | sales | Drawing | 0 |
| tbl_drawing_categories | sales | DrawingCategory | 2 |
| tbl_payment_methods | finance | PaymentMethod | 4 |
| tbl_debtors | credit | Debtor | 5 |
| tbl_debts | credit | Debt | 100 |
| tbl_debt_returns | credit | DebtReturn | 191 |
| tbl_expense_types | finance | ExpenseType | 6 |
| tbl_expense_items | finance | ExpenseItem | 7 |
| tbl_expense_rates | finance | ExpenseRate | 4 |
| tbl_recurrence_patterns | finance | RecurrencePattern | 4 |
| tbl_payment_obligations | finance | PaymentObligation | 102 |
| tbl_payments | finance | Payment | 23 |
| tbl_prepayments | finance | Prepayment | 4 |
| tbl_payment_allocations | finance | PaymentAllocation | 16 |
| tbl_liability_categories | finance | LiabilityCategory | 2 |
| tbl_liability_types | finance | LiabilityType | 4 |
| tbl_liability_items | finance | LiabilityItem | 1 |
| tbl_liability_payment_details | finance | LiabilityPaymentDetail | 0 |
| tbl_asset_categories | assets | AssetCategory | 2 |
| tbl_asset_types | assets | AssetType | 7 |
| tbl_assets | assets | Asset | 8 |

### Fields to DROP in Django (denormalized, derived)

These Access fields exist only because Access SQL cannot easily compute them inline. **Do not migrate these columns** — derive them in Django with ORM annotations:

- `month_id` → `ExtractMonth('sale_date')`
- `month_name` → `TruncMonth('sale_date')` + Python format
- `amount` on all transaction tables → computed property `quantity * unit_price - discount`
- `current_balance` on `tbl_liability_items` → computed from payment history
- `amount_remaining` on `tbl_prepayments` → `total_prepaid - amount_utilized`
- `balance` on `tbl_payment_obligations` → `amount_due - prepayment_applied - amount_paid`

---

## 4. Django App Architecture

```
kiyabo_duka/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── catalog/        # Products, categories, specs, brands, units
│   ├── inventory/      # Suppliers, purchases, purchase details, returns outward
│   ├── sales/          # Sales, return inwards, office use, drawings
│   ├── credit/         # Debtors, debts (credit sales), debt returns
│   ├── finance/        # Expenses, liabilities, payments, obligations, prepayments
│   ├── assets/         # Fixed assets register
│   ├── reports/        # Accounting engine, report views, PDF generation
│   └── dashboard/      # Home dashboard, KPIs, charts
│
├── templates/
│   ├── base.html
│   ├── catalog/
│   ├── inventory/
│   ├── sales/
│   ├── credit/
│   ├── finance/
│   ├── assets/
│   ├── reports/
│   └── dashboard/
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
├── manage.py
└── requirements/
    ├── base.txt
    └── production.txt
```

### App Responsibilities

**`catalog`** — Read-heavy master data. Products, brands, categories, specs. Changes rarely. Django Admin handles all CRUD. No custom views needed initially.

**`inventory`** — Purchasing workflow. Purchases are header + line items (formset pattern). Purchase returns linked to specific purchase detail lines.

**`sales`** — The busiest app. Every sale, office use, drawing, and sales return lives here. The POS-style sales entry form is the most important custom view in the system.

**`credit`** — Debtor management. Credit sales (debts) and repayment tracking (debt_returns). Aging analysis views.

**`finance`** — The most complex app. Expense items with recurrence, obligation generation, payments, prepayments, allocations, liabilities. Management command for obligation generation.

**`assets`** — Simple CRUD for fixed assets. Django Admin sufficient.

**`reports`** — No models. Pure service layer + views. Income statement, stock report, debtor aging, expense summary, payment summary. All views produce HTML (browser) or PDF (WeasyPrint).

**`dashboard`** — Homepage KPIs. Reads from all other apps. No models.

---

## 5. Models

### apps/catalog/models.py

```python
from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductType(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = [['category', 'name']]
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.abbreviation or self.name


class Spec(models.Model):
    """Spec dimension — e.g., 'Size', 'Color', 'Material'"""
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SpecValue(models.Model):
    """Concrete spec value — e.g., 'A4', 'Blue', 'Plastic'"""
    spec = models.ForeignKey(Spec, on_delete=models.PROTECT, related_name='values')
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = [['spec', 'value']]
        ordering = ['spec__name', 'value']

    def __str__(self):
        return f"{self.spec.name}: {self.value}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image_path = models.CharField(max_length=255, blank=True)  # legacy 'path' field

    class Meta:
        unique_together = [['name', 'product_type', 'brand']]
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def category(self):
        return self.product_type.category


class ProductSpec(models.Model):
    """
    A specific variant of a product — the sellable/purchasable unit.
    e.g., "A4 Notebook" (product) + "Blue" (spec_value) = one ProductSpec.
    Every transaction references a ProductSpec, not a Product.
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='specs')
    spec_value = models.ForeignKey(SpecValue, on_delete=models.PROTECT, related_name='product_specs')
    default_cost_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    default_selling_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reorder_level = models.PositiveIntegerField(default=5)
    current_stock = models.IntegerField(default=0)

    class Meta:
        unique_together = [['product', 'spec_value']]
        ordering = ['product__name', 'spec_value__value']

    def __str__(self):
        return f"{self.product.name} ({self.spec_value.value})"

    def update_stock(self):
        """
        Recalculate current_stock from all transaction tables.
        Call after any transaction that affects this product spec.
        Mirrors modStockCRUD.UpdateProductsStock().
        """
        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        def _sum(qs):
            return qs.aggregate(t=Coalesce(Sum('quantity'), 0))['t']

        from apps.inventory.models import PurchaseDetail, ReturnOutward
        from apps.sales.models import Sale, ReturnInward, SaleOfficeUse, Drawing
        from apps.credit.models import Debt

        purchased = _sum(PurchaseDetail.objects.filter(product_spec=self))
        ret_in = _sum(ReturnInward.objects.filter(sale__product_spec=self))
        sold = _sum(Sale.objects.filter(product_spec=self))
        credit = _sum(Debt.objects.filter(product_spec=self))
        ret_out = _sum(ReturnOutward.objects.filter(purchase_detail__product_spec=self))
        office = _sum(SaleOfficeUse.objects.filter(product_spec=self))
        drawings = _sum(Drawing.objects.filter(product_spec=self))

        self.current_stock = purchased + ret_in - sold - credit - ret_out - office - drawings
        self.save(update_fields=['current_stock'])

    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.current_stock <= 0
```

### apps/inventory/models.py

```python
from django.db import models
from django.utils import timezone
from apps.catalog.models import ProductSpec


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases')
    purchase_date = models.DateTimeField(default=timezone.now)
    invoice_number = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-purchase_date']

    def __str__(self):
        return f"Purchase #{self.pk} — {self.supplier.name} ({self.purchase_date.date()})"

    @property
    def total_amount(self):
        return sum(d.amount for d in self.details.all())

    @property
    def period_label(self):
        return self.purchase_date.strftime('%B %Y')


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='details')
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='purchase_details')
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    suggested_selling_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['product_spec__product__name']

    def __str__(self):
        return f"{self.product_spec} × {self.quantity} @ {self.unit_cost}"

    @property
    def amount(self):
        return self.quantity * self.unit_cost

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()


class ReturnOutward(models.Model):
    """Purchase return — goods sent back to supplier."""
    purchase_detail = models.ForeignKey(PurchaseDetail, on_delete=models.PROTECT, related_name='returns')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField(blank=True)
    sale_date = models.DateTimeField(default=timezone.now)  # kept as 'sale_date' for migration compat

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"Return Outward #{self.pk}"

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.purchase_detail.product_spec.update_stock()
```

### apps/sales/models.py

```python
from django.db import models
from django.utils import timezone
from apps.catalog.models import ProductSpec
from apps.finance.models import PaymentMethod


class Sale(models.Model):
    """Direct cash sale at the counter."""
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='sales')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"Sale #{self.pk} — {self.product_spec} ({self.sale_date.date()})"

    @property
    def amount(self):
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()


class ReturnInward(models.Model):
    """Sales return — customer returns goods."""
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='returns')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField(blank=True)
    sale_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-sale_date']

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sale.product_spec.update_stock()


class OfficeUseCategory(models.Model):
    """e.g., 'Customer Care', 'Display', 'Staff Use'"""
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Office Use Categories'

    def __str__(self):
        return self.name


class SaleOfficeUse(models.Model):
    """Internal product consumption — office use / customer care."""
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='office_uses')
    original_sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='office_use_conversions')
    office_use_category = models.ForeignKey(OfficeUseCategory, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Sale — Office Use'
        verbose_name_plural = 'Sales — Office Use'

    @property
    def amount(self):
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()


class DrawingCategory(models.Model):
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Drawing Categories'

    def __str__(self):
        return self.name


class Drawing(models.Model):
    """Owner withdrawals — goods taken for personal use."""
    drawing_category = models.ForeignKey(DrawingCategory, on_delete=models.PROTECT)
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='drawings')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-sale_date']

    @property
    def amount(self):
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()
```

### apps/credit/models.py

```python
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from apps.catalog.models import ProductSpec
from apps.finance.models import PaymentMethod


class Debtor(models.Model):
    """Credit customer (accounts receivable party)."""
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone_1 = models.CharField(max_length=30, blank=True)
    phone_2 = models.CharField(max_length=30, blank=True)
    nida_id = models.CharField(max_length=255, blank=True, verbose_name='NIDA ID')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_debt(self):
        return self.debts.aggregate(
            t=Coalesce(Sum('amount_due'), Decimal('0'))
        )['t']

    @property
    def total_paid(self):
        return DebtReturn.objects.filter(debt__debtor=self).aggregate(
            t=Coalesce(Sum('amount'), Decimal('0'))
        )['t']

    @property
    def outstanding_balance(self):
        return self.total_debt - self.total_paid


class Debt(models.Model):
    """A single credit sale line — creates an accounts receivable."""
    debtor = models.ForeignKey(Debtor, on_delete=models.PROTECT, related_name='debts')
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='debts')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    expected_payment_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Credit Sale (Debt)'

    def __str__(self):
        return f"Credit Sale #{self.pk} — {self.debtor.name}"

    @property
    def amount_due(self):
        return (self.quantity * self.unit_price) - self.discount

    @property
    def total_returned(self):
        return self.returns.aggregate(
            t=Coalesce(Sum('amount'), Decimal('0'))
        )['t']

    @property
    def balance(self):
        return self.amount_due - self.total_returned

    @property
    def is_overdue(self):
        from django.utils import timezone
        if not self.expected_payment_date:
            return False
        return self.balance > 0 and self.expected_payment_date < timezone.now().date()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()


class DebtReturn(models.Model):
    """Partial or full repayment against a credit sale."""
    debt = models.ForeignKey(Debt, on_delete=models.PROTECT, related_name='returns')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    return_date = models.DateTimeField(default=timezone.now)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-return_date']
        verbose_name = 'Debt Repayment'

    def __str__(self):
        return f"Repayment #{self.pk} — {self.debt.debtor.name} — {self.amount}"
```

### apps/finance/models.py

```python
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class PaymentMethod(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ExpenseType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ExpenseItem(models.Model):
    """A specific recurring expense — e.g., 'Shop Rent', 'Electricity Bill'."""
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['expense_type__name', 'name']

    def __str__(self):
        return f"{self.expense_type.name} — {self.name}"

    def current_rate(self) -> Decimal:
        """Returns the rate effective as of today."""
        rate = self.rates.filter(
            effective_from__lte=timezone.now().date()
        ).order_by('-effective_from').first()
        return rate.amount if rate else Decimal('0')


class ExpenseRate(models.Model):
    """Historical rate log — rate changes are tracked, not overwritten."""
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.CASCADE, related_name='rates')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    effective_from = models.DateField()
    change_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.expense_item.name} — {self.amount} from {self.effective_from}"


class RecurrencePattern(models.Model):
    """Defines how often an expense obligation is generated."""
    RECURRENCE_TYPES = [
        ('MONTHLY', 'Monthly'),
        ('WEEKLY', 'Weekly'),
        ('DAILY', 'Daily'),
        ('ONE_TIME', 'One Time'),
    ]
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.CASCADE, related_name='recurrences')
    recurrence_type = models.CharField(max_length=50, choices=RECURRENCE_TYPES)
    frequency_value = models.PositiveIntegerField(default=1)
    specific_day_of_week = models.IntegerField(null=True, blank=True)   # 1=Mon … 7=Sun; 0=last; negative=offset
    specific_day_of_month = models.IntegerField(default=-1)             # 1–31; 0=last; negative=offset from last
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['expense_item__name']

    def __str__(self):
        return f"{self.expense_item.name} — {self.recurrence_type}"

    def calculate_due_date(self, base_date) -> 'date':
        """
        Mirrors VBA CalculateDueDate() from modPayables.
        Supports last-day and negative offset conventions.
        """
        from datetime import date
        import calendar

        if self.recurrence_type == 'MONTHLY':
            last_day = calendar.monthrange(base_date.year, base_date.month)[1]
            dom = self.specific_day_of_month
            if dom is None or dom == 0:
                return date(base_date.year, base_date.month, last_day)
            elif dom < 0:
                from datetime import timedelta
                return date(base_date.year, base_date.month, last_day) + timedelta(days=dom)
            else:
                return date(base_date.year, base_date.month, min(dom, last_day))

        elif self.recurrence_type == 'WEEKLY':
            # Find the end of the week containing base_date, then apply offset
            from datetime import timedelta
            dow = self.specific_day_of_week or 1
            days_to_end_of_week = (7 - base_date.weekday()) % 7 or 7
            week_end = base_date + timedelta(days=days_to_end_of_week)
            if dow < 0:
                return week_end + timedelta(days=dow)
            return week_end

        return base_date


class PaymentObligation(models.Model):
    """
    Auto-generated obligation entry for each due expense/liability period.
    Generated by management command `generate_obligations`.
    Mirrors modPayables obligation generation logic.
    """
    OBLIGATION_TYPES = [('EXPENSE', 'Expense'), ('LIABILITY', 'Liability')]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]

    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='obligations')
    liability_item = models.ForeignKey('LiabilityItem', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='obligations')
    obligation_type = models.CharField(max_length=50, choices=OBLIGATION_TYPES)
    obligation_date = models.DateField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=15, decimal_places=2)
    prepayment_applied = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"Obligation #{self.pk} — {self.due_date} — {self.amount_due}"

    @property
    def balance(self):
        return self.amount_due - self.prepayment_applied - self.amount_paid

    @property
    def payment_status(self):
        if self.balance <= 0:
            return 'PAID'
        elif self.amount_paid > 0 or self.prepayment_applied > 0:
            return 'PARTIAL'
        elif self.due_date < timezone.now().date():
            return 'OVERDUE'
        return 'PENDING'


class Payment(models.Model):
    """Actual cash outflow against an obligation or directly against an expense/liability."""
    PAYMENT_TYPES = [('EXPENSE', 'Expense'), ('LIABILITY', 'Liability'), ('PREPAYMENT', 'Prepayment')]

    obligation = models.ForeignKey(PaymentObligation, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='payments')
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='payments')
    liability_item = models.ForeignKey('LiabilityItem', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='payments')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    payment_date = models.DateTimeField(default=timezone.now)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment #{self.pk} — {self.amount_paid} on {self.payment_date.date()}"


class Prepayment(models.Model):
    """Advance payment that can be allocated across future obligations."""
    STATUS_CHOICES = [('Active', 'Active'), ('Exhausted', 'Exhausted'), ('Cancelled', 'Cancelled')]

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='prepayments')
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='prepayments')
    liability_item = models.ForeignKey('LiabilityItem', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='prepayments')
    total_prepaid = models.DecimalField(max_digits=15, decimal_places=2)
    amount_utilized = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    prepayment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['-prepayment_date']

    def __str__(self):
        return f"Prepayment #{self.pk} — {self.total_prepaid}"

    @property
    def amount_remaining(self):
        return self.total_prepaid - self.amount_utilized


class PaymentAllocation(models.Model):
    """Links a prepayment to a specific obligation it covers."""
    prepayment = models.ForeignKey(Prepayment, on_delete=models.PROTECT, related_name='allocations')
    obligation = models.ForeignKey(PaymentObligation, on_delete=models.PROTECT, related_name='allocations')
    amount_allocated = models.DecimalField(max_digits=15, decimal_places=2)
    allocation_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-allocation_date']

    def __str__(self):
        return f"Allocation #{self.pk} — {self.amount_allocated}"


class LiabilityCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Liability Categories'

    def __str__(self):
        return self.name


class LiabilityType(models.Model):
    category = models.ForeignKey(LiabilityCategory, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class LiabilityItem(models.Model):
    """A specific external loan or long-term liability."""
    liability_type = models.ForeignKey(LiabilityType, on_delete=models.PROTECT, related_name='items')
    name = models.CharField(max_length=255)
    original_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    maturity_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    rate = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                help_text='Interest rate (e.g., 0.12 = 12%)')
    amount_per_return = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def current_balance(self):
        from django.db.models import Sum, Coalesce
        paid = self.payment_details.aggregate(
            t=Coalesce(Sum('principal_amount'), Decimal('0'))
        )['t']
        return self.original_amount - paid


class LiabilityPaymentDetail(models.Model):
    """Principal + interest breakdown for each liability payment."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='liability_details')
    liability_item = models.ForeignKey(LiabilityItem, on_delete=models.PROTECT,
                                        related_name='payment_details')
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Liability Payment #{self.pk} — {self.liability_item.name}"
```

### apps/assets/models.py

```python
from django.db import models
from django.utils import timezone


class AssetCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.name


class AssetType(models.Model):
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class Asset(models.Model):
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, related_name='assets')
    name = models.CharField(max_length=255)
    worth = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True)
    date_checked = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['asset_type__name', 'name']

    def __str__(self):
        return self.name
```

---

## 6. Services Layer

### VBA Module → Django Service Mapping

| VBA Module | Django Equivalent | Location |
|---|---|---|
| `modAccountings` | `AccountingService` | `apps/reports/services/accounting.py` |
| `modExpenses` | `ExpenseService` | `apps/finance/services/expenses.py` |
| `modPayables` | `PayableService` | `apps/finance/services/payables.py` |
| `modStockCRUD` | `ProductSpec.update_stock()` | `apps/catalog/models.py` |
| `modStats` | `StatsService` | `apps/reports/services/stats.py` |
| `modHelpers` | `get_default_*()` functions | `apps/catalog/utils.py` |
| `modFormsOPS` | Django URL redirects / `reverse()` | `urls.py` per app |
| `modFake` | `management/commands/generate_fake_data.py` | `apps/sales/` |
| `modSales.DeleteAllTransactions` | `management/commands/reset_transactions.py` | `apps/sales/` |

### Obligation Generator (replaces modPayables)

```python
# apps/finance/management/commands/generate_obligations.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import calendar
from apps.finance.models import RecurrencePattern, PaymentObligation, ExpenseItem


class Command(BaseCommand):
    help = 'Generate payment obligations from active recurrence patterns'

    def add_arguments(self, parser):
        parser.add_argument('--months', type=int, default=1,
                            help='Number of months ahead to generate (default: 1)')
        parser.add_argument('--from-date', type=str, default=None,
                            help='Start date YYYY-MM-DD (default: today)')

    def handle(self, *args, **options):
        from_date = date.today()
        if options['from_date']:
            from_date = date.fromisoformat(options['from_date'])

        months_ahead = options['months']
        # Compute end date
        end_month = from_date.month + months_ahead - 1
        end_year = from_date.year + (end_month - 1) // 12
        end_month = ((end_month - 1) % 12) + 1
        last_day = calendar.monthrange(end_year, end_month)[1]
        to_date = date(end_year, end_month, last_day)

        patterns = RecurrencePattern.objects.filter(
            is_active=True,
            expense_item__is_active=True,
            start_date__lte=to_date,
        ).exclude(end_date__lt=from_date).select_related('expense_item')

        created = 0
        for pattern in patterns:
            obligations = self._generate_for_pattern(pattern, from_date, to_date)
            created += len(obligations)

        self.stdout.write(self.style.SUCCESS(
            f'Generated {created} payment obligations up to {to_date}'
        ))

    def _generate_for_pattern(self, pattern, from_date, to_date):
        created = []
        current = pattern.start_date if pattern.start_date > from_date else from_date

        while current <= to_date:
            due_date = pattern.calculate_due_date(current)
            amount = pattern.expense_item.current_rate()

            # Skip if already exists (idempotent)
            exists = PaymentObligation.objects.filter(
                expense_item=pattern.expense_item,
                due_date=due_date,
                obligation_type='EXPENSE',
            ).exists()

            if not exists and amount > 0:
                obj = PaymentObligation.objects.create(
                    expense_item=pattern.expense_item,
                    obligation_type='EXPENSE',
                    obligation_date=current,
                    due_date=due_date,
                    amount_due=amount,
                    description=f'Auto-generated: {pattern.expense_item.name}',
                )
                created.append(obj)

            # Advance to next period
            if pattern.recurrence_type == 'MONTHLY':
                # Add one month
                month = current.month + 1
                year = current.year + (month - 1) // 12
                month = ((month - 1) % 12) + 1
                current = date(year, month, 1)
            elif pattern.recurrence_type == 'WEEKLY':
                current += timedelta(weeks=pattern.frequency_value)
            elif pattern.recurrence_type == 'DAILY':
                current += timedelta(days=pattern.frequency_value)
            else:
                break  # ONE_TIME

        return created
```

### Stock Reset Command (replaces modSales.DeleteAllTransactions)

```python
# apps/sales/management/commands/reset_transactions.py
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'DANGER: Delete all transaction data. Preserves master/setup data.'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true',
                            help='Required flag to actually run')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stderr.write('Dry run. Pass --confirm to actually delete.')
            return

        self.stdout.write(self.style.WARNING('Deleting all transactions...'))

        with transaction.atomic():
            from apps.credit.models import DebtReturn, Debt
            from apps.sales.models import ReturnInward, SaleOfficeUse, Drawing, Sale
            from apps.inventory.models import ReturnOutward, PurchaseDetail, Purchase
            from apps.finance.models import (
                PaymentAllocation, LiabilityPaymentDetail,
                Prepayment, Payment, PaymentObligation
            )
            from apps.catalog.models import ProductSpec

            DebtReturn.objects.all().delete()
            ReturnInward.objects.all().delete()
            ReturnOutward.objects.all().delete()
            SaleOfficeUse.objects.all().delete()
            Drawing.objects.all().delete()
            Debt.objects.all().delete()
            Sale.objects.all().delete()
            PurchaseDetail.objects.all().delete()
            Purchase.objects.all().delete()
            PaymentAllocation.objects.all().delete()
            LiabilityPaymentDetail.objects.all().delete()
            Prepayment.objects.all().delete()
            Payment.objects.all().delete()
            PaymentObligation.objects.all().delete()

            ProductSpec.objects.all().update(current_stock=0)

        self.stdout.write(self.style.SUCCESS('Done. All transactions deleted.'))
```

---

## 7. Forms and Views

### Complete Screen Inventory

Every Access form maps to a Django view. Forms marked ★ are high-priority custom views (not covered by Django Admin).

#### Catalog & Inventory

| Access Form | Django URL | View Type | Notes |
|---|---|---|---|
| frm_products_list | `/catalog/products/` | ListView | With search/filter |
| frm_product_detail | `/catalog/products/<pk>/` | DetailView | Stock, specs, prices |
| frm_product_new | `/catalog/products/new/` | CreateView | |
| frm_purchases ★ | `/inventory/purchases/` | ListView | |
| frm_purchase_new ★ | `/inventory/purchases/new/` | Custom CreateView + formset | Header + line items |
| frm_purchase_detail | `/inventory/purchases/<pk>/` | DetailView | |
| frm_return_outward_new | `/inventory/return-outwards/new/` | CreateView | |

#### Sales ★★ (Highest Priority)

| Access Form | Django URL | View Type | Notes |
|---|---|---|---|
| frm_sales_list | `/sales/` | ListView | Filter by date/product |
| frm_sales_single ★ | `/sales/new/` | Custom CreateView | POS-style entry |
| frm_sales_office_use_single ★ | `/sales/office-use/new/` | CreateView | |
| frm_drawings_new | `/sales/drawings/new/` | CreateView | |
| frm_return_inward_new | `/sales/return-inwards/new/` | CreateView | |

#### Credit Management

| Access Form | Django URL | View Type | Notes |
|---|---|---|---|
| frm_debtors_list | `/credit/debtors/` | ListView | Outstanding balances |
| frm_debtor_detail ★ | `/credit/debtors/<pk>/` | DetailView | All debts + repayments |
| frm_debt_new ★ | `/credit/debts/new/` | CreateView | Credit sale entry |
| frm_debt_return_new ★ | `/credit/debts/<debt_pk>/repay/` | CreateView | Record repayment |

#### Finance

| Access Form | Django URL | View Type | Notes |
|---|---|---|---|
| frm_expense_items | `/finance/expenses/` | ListView | |
| frm_expense_item_new | `/finance/expenses/new/` | CreateView | + rate + recurrence |
| frm_obligations_list ★ | `/finance/obligations/` | ListView | Due/overdue view |
| frm_payment_new ★ | `/finance/payments/new/` | CreateView | Pay obligation |
| frm_prepayment_new | `/finance/prepayments/new/` | CreateView | |
| frm_liabilities | `/finance/liabilities/` | ListView | |
| frm_liability_payment | `/finance/liabilities/<pk>/pay/` | CreateView | Principal+interest |

#### Reports ★★ (Accounting Grade)

| Report | Django URL | Output |
|---|---|---|
| Income Statement ★ | `/reports/income-statement/` | HTML + PDF |
| Stock Report ★ | `/reports/stock/` | HTML + PDF |
| Debtor Aging ★ | `/reports/debtor-aging/` | HTML + PDF |
| Expense Summary | `/reports/expenses/` | HTML + PDF |
| Payment History | `/reports/payments/` | HTML + PDF |
| Product Sales Analysis | `/reports/product-sales/` | HTML |
| Low Stock Alert | `/reports/low-stock/` | HTML |
| COGS Detail | `/reports/cogs-detail/` | HTML + PDF |

### Sales Entry View (frm_sales_single → /sales/new/)

This is the most critical form. It must be fast and forgiving:

```python
# apps/sales/views.py

from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import Sale
from .forms import SaleForm


class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:create')  # stay on form for fast repeated entry

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            # update_stock() is called in Sale.save() via signal/override
            messages.success(self.request,
                f"Sale recorded: {self.object.product_spec} × {self.object.quantity} "
                f"= TZS {self.object.amount:,.0f}")
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Show today's sales summary in sidebar
        from django.utils import timezone
        today = timezone.now().date()
        ctx['today_sales'] = Sale.objects.filter(
            sale_date__date=today
        ).select_related('product_spec__product')
        ctx['today_total'] = sum(s.amount for s in ctx['today_sales'])
        return ctx
```

```python
# apps/sales/forms.py

from django import forms
from .models import Sale
from apps.catalog.models import ProductSpec


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product_spec', 'quantity', 'unit_price', 'discount',
                  'payment_method', 'sale_date', 'notes']
        widgets = {
            'product_spec': forms.Select(attrs={'class': 'form-select select2'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'sale_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show in-stock products
        self.fields['product_spec'].queryset = (
            ProductSpec.objects
            .filter(current_stock__gt=0)
            .select_related('product', 'spec_value')
            .order_by('product__name')
        )
        # Pre-fill unit_price from default_selling_price via JS
        self.fields['unit_price'].required = True

    def clean(self):
        cleaned = super().clean()
        spec = cleaned.get('product_spec')
        qty = cleaned.get('quantity', 0)
        if spec and qty and qty > spec.current_stock:
            raise forms.ValidationError(
                f"Insufficient stock. Available: {spec.current_stock}, Requested: {qty}"
            )
        return cleaned
```

### Purchase Entry with Formset (header + line items)

```python
# apps/inventory/views.py

from django.views.generic import CreateView
from django.forms import inlineformset_factory
from django.db import transaction
from django.shortcuts import redirect
from .models import Purchase, PurchaseDetail
from .forms import PurchaseForm, PurchaseDetailForm


PurchaseDetailFormSet = inlineformset_factory(
    Purchase, PurchaseDetail,
    form=PurchaseDetailForm,
    fields=['product_spec', 'quantity', 'unit_cost', 'suggested_selling_price'],
    extra=5,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'inventory/purchase_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = PurchaseDetailFormSet(self.request.POST)
        else:
            ctx['formset'] = PurchaseDetailFormSet()
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['formset']
        if formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                # Stock updated automatically via PurchaseDetail.save()
            return redirect('inventory:purchase-detail', pk=self.object.pk)
        return self.render_to_response(ctx)
```

---

## 8. Reports

### Report Architecture

All reports follow the same pattern:
1. A view accepts GET parameters (date range, filters)
2. A service class computes the data
3. A template renders HTML
4. A `?format=pdf` query param triggers WeasyPrint PDF generation

```python
# apps/reports/views.py

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from datetime import date, datetime
from .services.accounting import AccountingService
from .services.expenses import ExpenseService


class IncomeStatementView(View):
    template_name = 'reports/income_statement.html'

    def get(self, request):
        # Date range from GET params, default = current month
        today = date.today()
        start_str = request.GET.get('start', today.replace(day=1).isoformat())
        end_str = request.GET.get('end', today.isoformat())

        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)

        svc = AccountingService(start, end)
        stmt = svc.to_income_statement()

        # Add expense breakdown
        exp_svc = ExpenseService(start, end)
        stmt['expenses'] = exp_svc.by_type()
        stmt['total_expenses'] = exp_svc.total()
        stmt['net_profit'] = stmt['gross_profit'] - stmt['total_expenses']

        ctx = {
            'stmt': stmt,
            'start': start,
            'end': end,
            'shop_name': 'Upendo Stationery',
        }

        if request.GET.get('format') == 'pdf':
            return self._render_pdf(request, ctx)
        return render(request, self.template_name, ctx)

    def _render_pdf(self, request, ctx):
        from weasyprint import HTML
        from django.template.loader import render_to_string
        html_string = render_to_string('reports/income_statement_pdf.html', ctx, request)
        pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'inline; filename="income_statement_{ctx["start"]}_{ctx["end"]}.pdf"'
        )
        return response
```

### Income Statement Template Prototype

```html
{# templates/reports/income_statement.html #}
{% extends "base.html" %}
{% block title %}Income Statement — {{ start }} to {{ end }}{% endblock %}

{% block content %}
<div class="container-fluid">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Income Statement</h2>
    <div>
      <a href="?start={{ start }}&end={{ end }}&format=pdf" class="btn btn-danger btn-sm">
        <i class="bi bi-file-pdf"></i> Export PDF
      </a>
    </div>
  </div>

  {# Date Range Filter #}
  <form method="get" class="row g-2 mb-4">
    <div class="col-auto">
      <label class="form-label">From</label>
      <input type="date" name="start" value="{{ start }}" class="form-control form-control-sm">
    </div>
    <div class="col-auto">
      <label class="form-label">To</label>
      <input type="date" name="end" value="{{ end }}" class="form-control form-control-sm">
    </div>
    <div class="col-auto align-self-end">
      <button type="submit" class="btn btn-primary btn-sm">Update</button>
    </div>
  </form>

  <div class="row">
    <div class="col-md-8">
      <div class="card">
        <div class="card-header text-center fw-bold">
          UPENDO STATIONERY<br>
          <small>Period: {{ start }} to {{ end }}</small>
        </div>
        <div class="card-body">

          {# REVENUE SECTION #}
          <table class="table table-sm table-borderless">
            <thead><tr><th colspan="3" class="text-uppercase text-muted small">Revenue</th></tr></thead>
            <tbody>
              <tr>
                <td class="ps-3">Direct Sales</td>
                <td></td>
                <td class="text-end">{{ stmt.direct_sales|floatformat:2 }}</td>
              </tr>
              <tr>
                <td class="ps-3">Credit Sales</td>
                <td></td>
                <td class="text-end">{{ stmt.credit_sales|floatformat:2 }}</td>
              </tr>
              <tr>
                <td class="ps-3 text-danger">Less: Return Inwards</td>
                <td></td>
                <td class="text-end text-danger">({{ stmt.return_inwards|floatformat:2 }})</td>
              </tr>
              <tr class="fw-bold border-top">
                <td>NET SALES</td>
                <td></td>
                <td class="text-end">{{ stmt.net_sales|floatformat:2 }}</td>
              </tr>
            </tbody>
          </table>

          {# COGS SECTION #}
          <table class="table table-sm table-borderless mt-2">
            <thead><tr><th colspan="3" class="text-uppercase text-muted small">Cost of Goods Sold</th></tr></thead>
            <tbody>
              <tr>
                <td class="ps-3">Opening Stock</td>
                <td class="text-end">{{ stmt.opening_stock|floatformat:2 }}</td>
                <td></td>
              </tr>
              <tr>
                <td class="ps-3">Add: Purchases</td>
                <td class="text-end">{{ stmt.purchases|floatformat:2 }}</td>
                <td></td>
              </tr>
              <tr>
                <td class="ps-3 text-danger">Less: Return Outwards</td>
                <td class="text-end text-danger">({{ stmt.return_outwards|floatformat:2 }})</td>
                <td></td>
              </tr>
              <tr>
                <td class="ps-3 fw-semibold">Net Purchases</td>
                <td class="text-end fw-semibold">{{ stmt.net_purchases|floatformat:2 }}</td>
                <td></td>
              </tr>
              <tr>
                <td class="ps-3">COGAS</td>
                <td class="text-end">{{ stmt.cogas|floatformat:2 }}</td>
                <td></td>
              </tr>
              <tr>
                <td class="ps-3 text-danger">Less: Closing Stock</td>
                <td class="text-end text-danger">({{ stmt.closing_stock|floatformat:2 }})</td>
                <td></td>
              </tr>
              <tr class="fw-bold border-top">
                <td>COST OF GOODS SOLD</td>
                <td></td>
                <td class="text-end">{{ stmt.cogs|floatformat:2 }}</td>
              </tr>
            </tbody>
          </table>

          {# GROSS PROFIT #}
          <div class="alert alert-{% if stmt.gross_profit >= 0 %}success{% else %}danger{% endif %} py-2">
            <div class="d-flex justify-content-between">
              <strong>GROSS PROFIT</strong>
              <strong>TZS {{ stmt.gross_profit|floatformat:2 }}</strong>
            </div>
          </div>

          {# EXPENSES SECTION #}
          <table class="table table-sm table-borderless mt-2">
            <thead><tr><th colspan="3" class="text-uppercase text-muted small">Operating Expenses</th></tr></thead>
            <tbody>
              {% for exp in stmt.expenses %}
              <tr>
                <td class="ps-3">{{ exp.name }}</td>
                <td></td>
                <td class="text-end">{{ exp.amount|floatformat:2 }}</td>
              </tr>
              {% empty %}
              <tr><td colspan="3" class="text-muted ps-3">No expenses recorded for period</td></tr>
              {% endfor %}
              <tr class="fw-bold border-top">
                <td>TOTAL OPERATING EXPENSES</td>
                <td></td>
                <td class="text-end">{{ stmt.total_expenses|floatformat:2 }}</td>
              </tr>
            </tbody>
          </table>

          {# NET PROFIT #}
          <div class="alert alert-{% if stmt.net_profit >= 0 %}primary{% else %}danger{% endif %} py-2">
            <div class="d-flex justify-content-between">
              <strong>NET PROFIT</strong>
              <strong>TZS {{ stmt.net_profit|floatformat:2 }}</strong>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### Debtor Aging Report

Aging analysis breaks outstanding balances into buckets: Current, 1–30 days, 31–60 days, 61–90 days, 90+ days. This is a key report for cash flow management.

```python
# apps/reports/services/debtor_aging.py

from datetime import date, timedelta
from decimal import Decimal
from apps.credit.models import Debtor, Debt, DebtReturn
from django.db.models import Sum
from django.db.models.functions import Coalesce


def debtor_aging_report(as_of: date = None) -> list:
    """
    Returns aging buckets for all debtors with outstanding balances.
    Buckets: Current (<= 0 days), 1-30, 31-60, 61-90, 90+
    """
    if as_of is None:
        as_of = date.today()

    report = []
    for debtor in Debtor.objects.prefetch_related('debts__returns').all():
        buckets = {
            'current': Decimal('0'),
            '1_30': Decimal('0'),
            '31_60': Decimal('0'),
            '61_90': Decimal('0'),
            '90_plus': Decimal('0'),
        }
        has_balance = False
        for debt in debtor.debts.all():
            balance = debt.balance
            if balance <= 0:
                continue
            has_balance = True
            if not debt.expected_payment_date:
                buckets['current'] += balance
                continue
            days_overdue = (as_of - debt.expected_payment_date).days
            if days_overdue <= 0:
                buckets['current'] += balance
            elif days_overdue <= 30:
                buckets['1_30'] += balance
            elif days_overdue <= 60:
                buckets['31_60'] += balance
            elif days_overdue <= 90:
                buckets['61_90'] += balance
            else:
                buckets['90_plus'] += balance

        if has_balance:
            total = sum(buckets.values())
            report.append({
                'debtor': debtor,
                'buckets': buckets,
                'total': total,
            })

    report.sort(key=lambda x: x['total'], reverse=True)
    return report
```

### Additional Reports Summary

| Report | Key Data | Django Annotations Used |
|---|---|---|
| **Stock Report** | All products, current_stock, reorder_level, WAC, stock value | `F()`, `annotate()`, `order_by('current_stock')` |
| **COGS Detail** | Per-product COGS breakdown | `AccountingService` per spec |
| **Expense Summary** | By type, by item, vs paid | `Sum()` on obligations and payments |
| **Payment History** | All payments with method breakdown | `values('payment_method__name').annotate()` |
| **Product Sales Analysis** | Top sellers, revenue by category/brand | `TruncMonth`, `annotate(Sum('amount'))` |
| **Low Stock Alerts** | Products below reorder level | `filter(current_stock__lte=F('reorder_level'))` |

---

## 9. Admin Configuration

Django Admin is your immediate CRUD interface for master data. Configure this first — it takes 2–3 hours and gives you a working system for all 33 tables.

```python
# apps/catalog/admin.py

from django.contrib import admin
from .models import Category, ProductType, Brand, Unit, Spec, SpecValue, Product, ProductSpec


class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_count']
    search_fields = ['name']
    inlines = [ProductTypeInline]

    def type_count(self, obj):
        return obj.types.count()
    type_count.short_description = 'Types'


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 0
    fields = ['spec_value', 'default_cost_price', 'default_selling_price',
              'reorder_level', 'current_stock']
    readonly_fields = ['current_stock']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'brand', 'unit', 'spec_count', 'total_stock']
    list_filter = ['product_type__category', 'brand']
    search_fields = ['name', 'brand__name']
    inlines = [ProductSpecInline]

    def spec_count(self, obj):
        return obj.specs.count()

    def total_stock(self, obj):
        return sum(s.current_stock for s in obj.specs.all())
    total_stock.short_description = 'Stock'


@admin.register(ProductSpec)
class ProductSpecAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'current_stock', 'is_low_stock', 'default_selling_price']
    list_filter = ['product__product_type__category', 'product__brand']
    search_fields = ['product__name', 'spec_value__value']
    readonly_fields = ['current_stock']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low?'
```

```python
# apps/inventory/admin.py

from django.contrib import admin
from .models import Supplier, Purchase, PurchaseDetail, ReturnOutward


class PurchaseDetailInline(admin.TabularInline):
    model = PurchaseDetail
    extra = 1
    fields = ['product_spec', 'quantity', 'unit_cost', 'suggested_selling_price']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'purchase_date', 'invoice_number', 'total_amount', 'item_count']
    list_filter = ['supplier', 'purchase_date']
    search_fields = ['supplier__name', 'invoice_number']
    inlines = [PurchaseDetailInline]
    date_hierarchy = 'purchase_date'

    def total_amount(self, obj):
        return f"TZS {obj.total_amount:,.0f}"

    def item_count(self, obj):
        return obj.details.count()
    item_count.short_description = 'Items'
```

```python
# apps/credit/admin.py

from django.contrib import admin
from .models import Debtor, Debt, DebtReturn


class DebtInline(admin.TabularInline):
    model = Debt
    extra = 0
    fields = ['product_spec', 'quantity', 'unit_price', 'sale_date', 'expected_payment_date']
    readonly_fields = ['sale_date']


class DebtReturnInline(admin.TabularInline):
    model = DebtReturn
    extra = 1
    fields = ['amount', 'payment_method', 'return_date', 'comment']


@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_1', 'outstanding_balance', 'nida_id']
    search_fields = ['name', 'phone_1', 'nida_id']
    inlines = [DebtInline]

    def outstanding_balance(self, obj):
        bal = obj.outstanding_balance
        return f"TZS {bal:,.0f}"
    outstanding_balance.short_description = 'Outstanding'


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['id', 'debtor', 'product_spec', 'amount_due', 'balance', 'expected_payment_date', 'is_overdue']
    list_filter = ['debtor', 'expected_payment_date']
    inlines = [DebtReturnInline]

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
```

```python
# apps/finance/admin.py

from django.contrib import admin
from .models import (
    PaymentMethod, ExpenseType, ExpenseItem, ExpenseRate,
    RecurrencePattern, PaymentObligation, Payment, Prepayment,
    PaymentAllocation, LiabilityCategory, LiabilityType,
    LiabilityItem, LiabilityPaymentDetail
)


class ExpenseRateInline(admin.TabularInline):
    model = ExpenseRate
    extra = 1
    ordering = ['-effective_from']


class RecurrencePatternInline(admin.StackedInline):
    model = RecurrencePattern
    extra = 0


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'expense_type', 'current_rate_display', 'is_active']
    list_filter = ['expense_type', 'is_active']
    inlines = [ExpenseRateInline, RecurrencePatternInline]

    def current_rate_display(self, obj):
        rate = obj.current_rate()
        return f"TZS {rate:,.0f}"
    current_rate_display.short_description = 'Current Rate'


@admin.register(PaymentObligation)
class PaymentObligationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'due_date', 'amount_due', 'balance', 'payment_status']
    list_filter = ['obligation_type', 'due_date']
    date_hierarchy = 'due_date'

    def get_name(self, obj):
        if obj.expense_item:
            return obj.expense_item.name
        if obj.liability_item:
            return obj.liability_item.name
        return '—'
    get_name.short_description = 'Item'
```

---

## 10. URL Structure

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Kiyabo Duka'
admin.site.site_title = 'Upendo Stationery'
admin.site.index_title = 'Shop Management'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls', namespace='dashboard')),
    path('catalog/', include('apps.catalog.urls', namespace='catalog')),
    path('inventory/', include('apps.inventory.urls', namespace='inventory')),
    path('sales/', include('apps.sales.urls', namespace='sales')),
    path('credit/', include('apps.credit.urls', namespace='credit')),
    path('finance/', include('apps.finance.urls', namespace='finance')),
    path('assets/', include('apps.assets.urls', namespace='assets')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
]
```

```python
# apps/sales/urls.py
from django.urls import path
from . import views

app_name = 'sales'
urlpatterns = [
    path('', views.SaleListView.as_view(), name='list'),
    path('new/', views.SaleCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.SaleDeleteView.as_view(), name='delete'),
    path('office-use/', views.OfficeUseListView.as_view(), name='office-use-list'),
    path('office-use/new/', views.OfficeUseCreateView.as_view(), name='office-use-create'),
    path('drawings/', views.DrawingListView.as_view(), name='drawing-list'),
    path('drawings/new/', views.DrawingCreateView.as_view(), name='drawing-create'),
    path('return-inwards/new/', views.ReturnInwardCreateView.as_view(), name='return-inward-create'),
]
```

```python
# apps/reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.ReportIndexView.as_view(), name='index'),
    path('income-statement/', views.IncomeStatementView.as_view(), name='income-statement'),
    path('stock/', views.StockReportView.as_view(), name='stock'),
    path('debtor-aging/', views.DebtorAgingView.as_view(), name='debtor-aging'),
    path('expenses/', views.ExpenseSummaryView.as_view(), name='expenses'),
    path('payments/', views.PaymentHistoryView.as_view(), name='payments'),
    path('product-sales/', views.ProductSalesView.as_view(), name='product-sales'),
    path('low-stock/', views.LowStockView.as_view(), name='low-stock'),
    path('cogs-detail/', views.COGSDetailView.as_view(), name='cogs-detail'),
]
```

---

## 11. Project Setup

### requirements/base.txt

```txt
Django>=5.1,<5.2
psycopg2-binary>=2.9
python-decouple>=3.8
weasyprint>=62.0
django-crispy-forms>=2.3
crispy-bootstrap5>=2024.2
Pillow>=10.0
python-dateutil>=2.8
django-extensions>=3.2
```

### requirements/production.txt

```txt
-r base.txt
gunicorn>=21.2
whitenoise>=6.7
django-storages>=1.14   # for S3/object storage if needed
sentry-sdk>=1.40        # error tracking
celery>=5.3             # async tasks / obligation generation
redis>=5.0              # celery broker
```

### config/settings/base.py

```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    # Local apps
    'apps.catalog',
    'apps.inventory',
    'apps.sales',
    'apps.credit',
    'apps.finance',
    'apps.assets',
    'apps.reports',
    'apps.dashboard',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='kiyabo_duka'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'

# Celery (obligation generation)
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_BEAT_SCHEDULE = {
    'generate-monthly-obligations': {
        'task': 'apps.finance.tasks.generate_obligations',
        'schedule': 86400,  # daily
    },
}
```

### One-Command Bootstrap

```bash
#!/bin/bash
# setup.sh — Run once to set up the project

python -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt

# Create apps directory structure
mkdir -p apps/{catalog,inventory,sales,credit,finance,assets,reports,dashboard}
for app in catalog inventory sales credit finance assets reports dashboard; do
    python manage.py startapp $app apps/$app
done

# Apply settings
cp config/settings/base.py.example config/settings/base.py
cp .env.example .env
# Edit .env: DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

---

## 12. Data Migration Checklist

You said you'll handle data migration yourself. Here is the exact sequence with notes on gotchas.

### Migration Order (strict — respects FK constraints)

```
Phase A — Lookup / Master Data (no FK dependencies)
  1. tbl_categories        → catalog_category
  2. tbl_brands            → catalog_brand
  3. tbl_units             → catalog_unit
  4. tbl_specs             → catalog_spec
  5. tbl_payment_methods   → finance_paymentmethod
  6. tbl_expense_types     → finance_expensetype
  7. tbl_drawing_categories → sales_drawingcategory
  8. tbl_office_use        → sales_officeusecat  (map 'office_use' → 'name')
  9. tbl_asset_categories  → assets_assetcategory
  10. tbl_liability_categories → finance_liabilitycategory

Phase B — Second-level lookups (FK → Phase A)
  11. tbl_types            → catalog_producttype   (FK: category_id)
  12. tbl_spec_values      → catalog_specvalue      (FK: spec_id)
  13. tbl_asset_types      → assets_assettype       (FK: asset_category_id)
  14. tbl_liability_types  → finance_liabilitytype  (FK: liability_category_id)

Phase C — Products & Entities
  15. tbl_products         → catalog_product        (FK: type_id, brand_id, unit_id)
  16. tbl_product_specs    → catalog_productspec    (FK: product_id, spec_value_id)
  17. tbl_suppliers        → inventory_supplier
  18. tbl_debtors          → credit_debtor
  19. tbl_assets           → assets_asset           (FK: asset_type_id)
  20. tbl_liability_items  → finance_liabilityitem  (FK: liability_type_id)
  21. tbl_expense_items    → finance_expenseitem    (FK: expense_type_id)

Phase D — Rates & Patterns
  22. tbl_expense_rates    → finance_expenserate    (FK: expense_item_id)
  23. tbl_recurrence_patterns → finance_recurrencepattern (FK: expense_item_id)

Phase E — Transactions (largest, most critical)
  24. tbl_purchases        → inventory_purchase     (FK: supplier_id)
  25. tbl_purchase_details → inventory_purchasedetail (FK: purchase_id, product_spec_id)
  26. tbl_sales            → sales_sale             (FK: product_spec_id, payment_method_id)
  27. tbl_debts            → credit_debt            (FK: debtor_id, product_spec_id)
  28. tbl_sales_office_use → sales_saleofficeuse    (FK: product_spec_id, office_use_id)
  29. tbl_drawings         → sales_drawing          (FK: drawing_category_id, product_spec_id)

Phase F — Returns (FK → transactions)
  30. tbl_return_inwards   → sales_returninward     (FK: sale_id)
  31. tbl_return_outwards  → inventory_returnoutward (FK: purchase_detail_id)
  32. tbl_debt_returns     → credit_debtreturn      (FK: debt_id, payment_method_id)

Phase G — Finance transactions
  33. tbl_payment_obligations → finance_paymentobligation
  34. tbl_payments         → finance_payment
  35. tbl_prepayments      → finance_prepayment
  36. tbl_payment_allocations → finance_paymentallocation
  37. tbl_liability_payment_details → finance_liabilitypaymentdetail
```

### Key Migration Notes

**Fields to DROP** — Do NOT migrate:
- `month_id`, `month_name` on all tables — derive from date fields in Django
- `amount` (computed) — use `@property` in Python
- `current_balance` (computed) — `@property`
- `amount_remaining` (computed) — `@property`
- `balance` (computed) — `@property`
- `payment_status` (computed) — `@property`

**Fields to RENAME:**
- `tbl_debtors.phone_number_1` → `credit_debtor.phone_1`
- `tbl_debtors.phone_number_2` → `credit_debtor.phone_2`
- `tbl_products.path` → `catalog_product.image_path`
- `tbl_sales_office_use.sales_sale_id` → `sales_saleofficeuse.original_sale_id`

**Post-migration: Recalculate all stock**
```bash
python manage.py shell -c "
from apps.catalog.models import ProductSpec
specs = ProductSpec.objects.all()
print(f'Updating stock for {specs.count()} specs...')
for spec in specs:
    spec.update_stock()
print('Done.')
"
```

**Validate accounting equation after migration:**
```bash
python manage.py shell -c "
from apps.reports.services.accounting import AccountingService
from datetime import date
svc = AccountingService(date(2026, 4, 1), date(2026, 4, 30))
stmt = svc.to_income_statement()
opening = stmt['opening_stock']
net_purch = stmt['net_purchases']
cogs = stmt['cogs']
closing = stmt['closing_stock']
lhs = opening + net_purch
rhs = cogs + closing
print(f'LHS: {lhs:,.2f}  RHS: {rhs:,.2f}  Match: {abs(lhs - rhs) < 0.01}')
"
```

---

## 13. Testing Strategy

### What Must Be Tested (Business-Critical)

```python
# apps/reports/tests/test_accounting.py

from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.catalog.tests.factories import ProductSpecFactory
from apps.inventory.tests.factories import PurchaseFactory, PurchaseDetailFactory
from apps.sales.tests.factories import SaleFactory
from apps.reports.services.accounting import AccountingService


class AccountingEquationTest(TestCase):
    """The accounting equation must always hold: Opening + Net Purchases = COGS + Closing"""

    def setUp(self):
        spec = ProductSpecFactory()
        # Purchase 100 units at 1000 TZS each
        purchase = PurchaseFactory(purchase_date=date(2026, 4, 1))
        PurchaseDetailFactory(purchase=purchase, product_spec=spec,
                              quantity=100, unit_cost=1000)
        # Sell 30 units at 1500 TZS each
        SaleFactory(product_spec=spec, quantity=30, unit_price=1500,
                    sale_date=date(2026, 4, 15))
        self.spec = spec

    def test_accounting_equation_holds(self):
        svc = AccountingService(date(2026, 4, 1), date(2026, 4, 30), self.spec.id)
        stmt = svc.to_income_statement()
        lhs = stmt['opening_stock'] + stmt['net_purchases']
        rhs = stmt['cogs'] + stmt['closing_stock']
        self.assertAlmostEqual(float(lhs), float(rhs), places=2)

    def test_cogs_weighted_average(self):
        svc = AccountingService(date(2026, 4, 1), date(2026, 4, 30), self.spec.id)
        # Purchased 100 @ 1000 = 100,000 total cost
        # WAC = 100,000 / 100 = 1,000
        # COGS = 30 × 1,000 = 30,000
        self.assertEqual(svc.cogs(), Decimal('30000.00'))

    def test_gross_profit(self):
        svc = AccountingService(date(2026, 4, 1), date(2026, 4, 30), self.spec.id)
        # Net Sales = 30 × 1,500 = 45,000
        # COGS = 30,000
        # Gross Profit = 15,000
        self.assertEqual(svc.gross_profit(), Decimal('15000.00'))


class StockUpdateTest(TestCase):
    """Stock must update correctly after every transaction."""

    def test_stock_after_purchase(self):
        spec = ProductSpecFactory(current_stock=0)
        purchase = PurchaseFactory()
        PurchaseDetailFactory(purchase=purchase, product_spec=spec, quantity=50, unit_cost=500)
        spec.refresh_from_db()
        self.assertEqual(spec.current_stock, 50)

    def test_stock_after_sale(self):
        spec = ProductSpecFactory(current_stock=50)
        SaleFactory(product_spec=spec, quantity=10, unit_price=600)
        spec.refresh_from_db()
        self.assertEqual(spec.current_stock, 40)

    def test_stock_cannot_go_negative_via_form(self):
        spec = ProductSpecFactory(current_stock=5)
        from apps.sales.forms import SaleForm
        form = SaleForm(data={
            'product_spec': spec.pk,
            'quantity': 10,  # more than available
            'unit_price': 600,
            'discount': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Insufficient stock', str(form.errors))
```

### Test Factories (using factory_boy)

```python
# apps/catalog/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from apps.catalog.models import Category, ProductType, Brand, Unit, Spec, SpecValue, Product, ProductSpec


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
    name = factory.Sequence(lambda n: f'Category {n}')


class ProductTypeFactory(DjangoModelFactory):
    class Meta:
        model = ProductType
    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f'Type {n}')


class BrandFactory(DjangoModelFactory):
    class Meta:
        model = Brand
    name = factory.Sequence(lambda n: f'Brand {n}')


class SpecFactory(DjangoModelFactory):
    class Meta:
        model = Spec
    name = 'Size'


class SpecValueFactory(DjangoModelFactory):
    class Meta:
        model = SpecValue
    spec = factory.SubFactory(SpecFactory)
    value = factory.Sequence(lambda n: f'Value {n}')


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
    name = factory.Sequence(lambda n: f'Product {n}')
    product_type = factory.SubFactory(ProductTypeFactory)
    brand = factory.SubFactory(BrandFactory)


class ProductSpecFactory(DjangoModelFactory):
    class Meta:
        model = ProductSpec
    product = factory.SubFactory(ProductFactory)
    spec_value = factory.SubFactory(SpecValueFactory)
    default_selling_price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    current_stock = 100
```

---

## 14. Deployment

### Production Stack

```
Internet → Nginx (reverse proxy + static files)
              ↓
          Gunicorn (Django WSGI)
              ↓
          PostgreSQL 16
              ↓
          Redis (Celery broker for obligation generation)
```

### Nginx Config

```nginx
server {
    listen 80;
    server_name duka.yourdomain.com;

    location /static/ {
        alias /var/www/kiyabo_duka/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/kiyabo_duka/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Gunicorn Systemd Service

```ini
[Unit]
Description=Kiyabo Duka Django
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/kiyabo_duka
ExecStart=/var/www/kiyabo_duka/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### .env (production)

```bash
SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=duka.yourdomain.com,localhost
DB_NAME=kiyabo_duka
DB_USER=kiyabo_user
DB_PASSWORD=<strong-password>
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

### Deployment Runbook

```bash
# First deploy
git clone https://github.com/youruser/kiyabo_duka.git /var/www/kiyabo_duka
cd /var/www/kiyabo_duka
python -m venv venv
source venv/bin/activate
pip install -r requirements/production.txt
cp .env.example .env  # fill in values
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
sudo systemctl enable kiyabo_duka
sudo systemctl start kiyabo_duka

# Subsequent deploys
git pull
pip install -r requirements/production.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart kiyabo_duka
```

### Backup Strategy

```bash
# Daily database backup (add to cron)
pg_dump kiyabo_duka | gzip > /backups/kiyabo_duka_$(date +%Y%m%d_%H%M%S).sql.gz

# Or via Django dumpdata (slower but portable)
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude=contenttypes --exclude=auth.permission \
    > /backups/kiyabo_duka_$(date +%Y%m%d).json

# Keep last 30 days
find /backups -name "*.sql.gz" -mtime +30 -delete
```

---

## Appendix A: VBA → Python Glossary

| VBA Pattern | Python/Django Equivalent |
|---|---|
| `Nz(DSum("amount", "tbl_sales", condition), 0)` | `Sale.objects.filter(...).aggregate(t=Coalesce(Sum('amount'), 0))['t']` |
| `DLookup("unit_id", "tbl_units", "unit_name='piece'")` | `Unit.objects.filter(name='piece').values_list('unit_id', flat=True).first()` |
| `Format(Date(), "mm/dd/yyyy")` | `timezone.now().date().strftime('%d/%m/%Y')` |
| `IsDate(upToDate)` | `isinstance(up_to_date, date)` |
| `rs.AddNew … rs.Update` | `obj = Model(**fields); obj.save()` |
| `db.Execute "DELETE FROM …"` | `Model.objects.all().delete()` |
| `ws.BeginTrans … ws.CommitTrans` | `with transaction.atomic():` |
| `ws.Rollback` | Automatic on exception inside `transaction.atomic()` |
| `DateDiff("d", date1, date2)` | `(date2 - date1).days` |
| `DateSerial(Year, Month+1, 0)` | `calendar.monthrange(year, month)[1]` |
| `IIf(condition, truepart, falsepart)` | `truepart if condition else falsepart` |
| `MsgBox "msg", vbInformation` | `messages.success(request, 'msg')` |
| `DoCmd.OpenForm "frm_name"` | `redirect(reverse('app:view-name'))` |
| `month_id` field on tables | `ExtractMonth('sale_date')` annotation |
| `month_name` field on tables | `TruncMonth('sale_date')` + `.strftime('%B %Y')` |

---

## Appendix B: Key Business Rules (Do Not Lose These)

1. **Stock can never go below zero via a user transaction** — validated at form level (`SaleForm.clean()`).

2. **Weighted average cost, not FIFO** — COGS = `total_purchase_cost / total_purchased_qty × qty_outflowed`. Must be consistent across all report periods.

3. **Accounting equation must always hold** — `Opening Stock + Net Purchases = COGS + Closing Stock`. Run as a nightly integrity check.

4. **Credit sales reduce stock immediately** — same as direct sales for stock purposes. Revenue is also recognized immediately (accrual basis).

5. **Return Inwards increase stock but do NOT add to purchases** — they reverse a sale, not add a purchase.

6. **Return Outwards decrease stock but do NOT increase sales returns** — they reverse a purchase cost.

7. **Office Use and Drawings are both included in COGS** — they represent goods leaving inventory even though no revenue was generated.

8. **Expense obligations are auto-generated from recurrence patterns** — the `generate_obligations` management command must run daily (Celery beat or cron).

9. **A prepayment can cover multiple future obligations** — the `PaymentAllocation` table links one prepayment to many obligations. The `amount_utilized` on `Prepayment` must always equal `SUM(amount_allocated)` for that prepayment.

10. **Liability payments split into principal + interest** — stored separately in `LiabilityPaymentDetail`. The `LiabilityItem.current_balance` property deducts only principal, not interest.

11. **Expected payment date on debts is for aging analysis** — it does not automatically generate an obligation. Aging is computed dynamically in the report service.

12. **`month_id` and `month_name` are denormalized artifacts** — in Django, derive period labels from `sale_date` at query time. Never store them.

---

## Appendix C: Dashboard KPIs

The home dashboard should show these KPIs, all computable from the services:

```python
# apps/dashboard/views.py

from django.views.generic import TemplateView
from django.utils import timezone
from apps.catalog.models import ProductSpec
from apps.sales.models import Sale
from apps.credit.models import Debt, DebtReturn
from apps.finance.models import PaymentObligation
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import Coalesce
from decimal import Decimal


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        month_start = today.replace(day=1)

        # Today's sales
        today_sales = Sale.objects.filter(sale_date__date=today)
        ctx['today_revenue'] = today_sales.aggregate(
            t=Coalesce(Sum('amount'), Decimal('0'))
        )['t']
        ctx['today_transactions'] = today_sales.count()

        # This month's sales
        month_sales = Sale.objects.filter(sale_date__date__gte=month_start)
        ctx['month_revenue'] = month_sales.aggregate(
            t=Coalesce(Sum('amount'), Decimal('0'))
        )['t']

        # Outstanding debt (accounts receivable)
        from apps.credit.models import Debtor
        total_debts = Debt.objects.aggregate(t=Coalesce(Sum('amount_due'), Decimal('0')))['t']
        total_repaid = DebtReturn.objects.aggregate(t=Coalesce(Sum('amount'), Decimal('0')))['t']
        ctx['total_receivables'] = max(total_debts - total_repaid, Decimal('0'))
        ctx['overdue_count'] = sum(1 for d in Debt.objects.all() if d.is_overdue)

        # Low stock alerts
        ctx['low_stock_count'] = ProductSpec.objects.filter(
            current_stock__lte=F('reorder_level')
        ).count()
        ctx['out_of_stock_count'] = ProductSpec.objects.filter(
            current_stock__lte=0
        ).count()

        # Overdue obligations
        ctx['overdue_obligations'] = PaymentObligation.objects.filter(
            due_date__lt=today,
            amount_paid__lt=F('amount_due'),
        ).count()

        return ctx
```

---

*Document: Kiyabo Duka Django Migration Master Plan*  
*Version: 1.0 — May 2026*  
*Authors: Derived from full analysis of Kiyabo Duka v0.031 source (schema, 9 VBA modules, live P&L)*  
*This document is the single source of truth for the Django migration. Update it as decisions are made.*
