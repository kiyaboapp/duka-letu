# Kiyabo Duka — Programmer's Implementation Guide
## Reports System, Payment Method Architecture & Period Engine
### Stack: Django 5.x · PostgreSQL 16 · WeasyPrint · Bootstrap 5
### Version: 1.0 — May 2026

---

> **Who this document is for:** The developer building the `reports` app and the payment method system. You should have already read the Django Master Plan and the Accounting Reports Reference. This document tells you *exactly* what to build, in what order, and how each piece connects. No accounting theory here — just engineering decisions, code structure, and the reasoning behind them.

---

## PART 1 — PAYMENT METHOD ARCHITECTURE

### 1.1 The Problem With The Current Model

`PaymentMethod` in the master plan is this:

```python
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255, unique=True)
```

Four records exist: the Access database shows `tbl_payment_methods` has 4 rows. Those four are almost certainly: Cash, M-Pesa, and two others. There is no structure — no category, no behaviour flag, nothing. Every piece of code that needs to know "is this cash or mobile money?" is forced to do a string comparison against the name. That is the root of the M-Pesa hardcoding problem.

### 1.2 The Right Structure: Three Levels

Payment methods have a natural three-level hierarchy that mirrors how money actually moves:

```
PaymentCategory          PaymentProvider            PaymentMethod
(the type of money)      (who operates it)          (the specific channel)

CASH ──────────────────► [no provider needed] ────► Cash

MOBILE_MONEY ──────────► Vodacom ──────────────────► M-Pesa
                       ► Tigo ────────────────────► Tigo Pesa
                       ► Airtel ──────────────────► Airtel Money
                       ► Halopesa ────────────────► Halopesa

BANK ───────────────────► CRDB ────────────────────► CRDB Direct Transfer
                       ► CRDB ────────────────────► CRDB Cheque
                       ► NMB ─────────────────────► NMB Direct Transfer
                       ► NMB ─────────────────────► NMB Cheque
                       ► NBC ─────────────────────► NBC Direct Transfer
```

**Why provider matters:**
When a mobile money payment fails to settle, you need to know which network to call. When a cheque bounces, you need to know which bank issued it. The provider is the real-world entity you contact. The category is what the code filters by. The method is what the user selects when entering a transaction.

**The cheque vs. bank distinction resolved:**
Both are `BANK` category. The difference is `clears_immediately`. A CRDB direct transfer: `clears_immediately=True`. A CRDB cheque: `clears_immediately=False`. Same category, same provider, different clearing behaviour. This is the correct model — not a separate `CHEQUE` category.

### 1.3 The Three Models

```python
# apps/finance/models.py — FULL REPLACEMENT of PaymentMethod

class PaymentCategory(TimestampedModel):
    """
    Top-level type of money movement. Code always filters by category — never by name.
    This is what controls business logic:
      CASH         → affects physical till count
      MOBILE_MONEY → affects mobile wallet balance
      BANK         → affects bank account; may have clearing delay (cheques)
    """
    CATEGORY_CODES = [
        ('CASH',         'Physical Cash'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK',         'Bank / Cheque'),
    ]
    code = models.CharField(
        max_length=20, choices=CATEGORY_CODES, unique=True,
        help_text='Fixed code used in all business logic filtering. Never change this.'
    )
    name = models.CharField(max_length=100)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Payment Category'
        verbose_name_plural = 'Payment Categories'

    def __str__(self):
        return self.name


class PaymentProvider(TimestampedModel):
    """
    The institution or network that operates the payment channel.
    e.g. Vodacom, CRDB Bank, NMB Bank, Airtel.
    Cash has no provider — leave provider null for CASH methods.
    """
    category = models.ForeignKey(
        PaymentCategory, on_delete=models.PROTECT, related_name='providers'
    )
    name = models.CharField(max_length=255, unique=True)
    short_code = models.CharField(
        max_length=20, blank=True,
        help_text='Optional short identifier. e.g. CRDB, NMB, VOD'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category__display_order', 'name']
        verbose_name = 'Payment Provider'

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class PaymentMethod(TimestampedModel):
    """
    The specific channel the cashier selects when recording a transaction.
    e.g. 'M-Pesa', 'CRDB Direct Transfer', 'NMB Cheque', 'Cash'.

    This replaces the old single-field PaymentMethod.
    All existing FK references to PaymentMethod remain valid —
    only the model itself gains structure.

    CRITICAL: Code must NEVER filter by PaymentMethod.name.
    Always filter by PaymentMethod.category.code or clears_immediately.
    """
    category = models.ForeignKey(
        PaymentCategory, on_delete=models.PROTECT, related_name='methods'
    )
    provider = models.ForeignKey(
        PaymentProvider, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='methods',
        help_text='Null for Cash — cash has no provider.'
    )
    name = models.CharField(
        max_length=255, unique=True,
        help_text='Human-readable name shown in forms. e.g. "M-Pesa", "CRDB Cheque"'
    )
    clears_immediately = models.BooleanField(
        default=True,
        help_text=(
            'True for Cash, all Mobile Money, and direct bank transfers. '
            'False for cheques — funds are unconfirmed until bank clears them '
            '(typically 1–3 business days). '
            'Uncleared amounts are shown separately in the cash reconciliation '
            'and appear as "Cheques in Transit" on the Balance Sheet, '
            'not in Cash & Equivalents.'
        )
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category__display_order', 'provider__name', 'name']
        verbose_name = 'Payment Method'

    def __str__(self):
        return self.name

    @property
    def is_cash(self) -> bool:
        return self.category.code == 'CASH'

    @property
    def is_mobile_money(self) -> bool:
        return self.category.code == 'MOBILE_MONEY'

    @property
    def is_bank(self) -> bool:
        return self.category.code == 'BANK'
```

### 1.4 Seed Data Command

```python
# apps/finance/management/commands/seed_payment_methods.py

from django.core.management.base import BaseCommand
from apps.finance.models import PaymentCategory, PaymentProvider, PaymentMethod


SEED = [
    # (category_code, provider_name, method_name, clears_immediately)
    ('CASH',         None,            'Cash',                  True),
    ('MOBILE_MONEY', 'Vodacom',       'M-Pesa',                True),
    ('MOBILE_MONEY', 'Tigo',          'Tigo Pesa',             True),
    ('MOBILE_MONEY', 'Airtel',        'Airtel Money',          True),
    ('MOBILE_MONEY', 'Halopesa',      'Halopesa',              True),
    ('BANK',         'CRDB Bank',     'CRDB Direct Transfer',  True),
    ('BANK',         'CRDB Bank',     'CRDB Cheque',           False),
    ('BANK',         'NMB Bank',      'NMB Direct Transfer',   True),
    ('BANK',         'NMB Bank',      'NMB Cheque',            False),
    ('BANK',         'NBC Bank',      'NBC Direct Transfer',   True),
    ('BANK',         'NBC Bank',      'NBC Cheque',            False),
]

CATEGORIES = [
    ('CASH',         'Cash',         0),
    ('MOBILE_MONEY', 'Mobile Money', 1),
    ('BANK',         'Bank',         2),
]

PROVIDERS = {
    'Vodacom':   'MOBILE_MONEY',
    'Tigo':      'MOBILE_MONEY',
    'Airtel':    'MOBILE_MONEY',
    'Halopesa':  'MOBILE_MONEY',
    'CRDB Bank': 'BANK',
    'NMB Bank':  'BANK',
    'NBC Bank':  'BANK',
}


class Command(BaseCommand):
    help = 'Seed payment categories, providers, and methods.'

    def handle(self, *args, **options):
        # 1. Categories
        cat_map = {}
        for code, name, order in CATEGORIES:
            cat, _ = PaymentCategory.objects.update_or_create(
                code=code, defaults={'name': name, 'display_order': order}
            )
            cat_map[code] = cat
            self.stdout.write(f'  Category: {cat}')

        # 2. Providers
        prov_map = {}
        for pname, cat_code in PROVIDERS.items():
            prov, _ = PaymentProvider.objects.update_or_create(
                name=pname, defaults={'category': cat_map[cat_code]}
            )
            prov_map[pname] = prov
            self.stdout.write(f'  Provider: {prov}')

        # 3. Methods
        for cat_code, prov_name, method_name, clears in SEED:
            provider = prov_map.get(prov_name)
            method, created = PaymentMethod.objects.update_or_create(
                name=method_name,
                defaults={
                    'category': cat_map[cat_code],
                    'provider': provider,
                    'clears_immediately': clears,
                }
            )
            label = 'Created' if created else 'Updated'
            self.stdout.write(f'  {label}: {method}')

        self.stdout.write(self.style.SUCCESS('Payment method seed complete.'))
```

### 1.5 Everywhere That Filters by Payment Method — Use Category Code

```python
# WRONG — breaks if someone renames M-Pesa to "Mpesa" or adds a typo
Sale.objects.filter(payment_method__name='M-Pesa')

# CORRECT — works for any mobile money provider now and in future
Sale.objects.filter(payment_method__category__code='MOBILE_MONEY')

# CORRECT — cash only
Sale.objects.filter(payment_method__category__code='CASH')

# CORRECT — only cleared bank payments (not cheques still in transit)
Sale.objects.filter(
    payment_method__category__code='BANK',
    payment_method__clears_immediately=True
)
```

### 1.6 SessionBalance — Replaces Hardcoded CashRegisterSession Fields

The daily reconciliation model stores one row per `PaymentMethod` per day. There are no hardcoded columns for M-Pesa or Cash.

```python
# apps/finance/models.py

class CashRegisterSession(TimestampedModel):
    session_date = models.DateField(unique=True)
    opened_by = models.CharField(max_length=255)
    closed_by = models.CharField(max_length=255, blank=True)
    opening_float = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text='Physical cash placed in till at start of day.'
    )
    variance_explanation = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('OPEN','Open'),('CLOSED','Closed'),('VARIANCE','Variance')],
        default='OPEN'
    )

    def closing_balance_for(self, category_code: str) -> Decimal:
        """
        Total physically confirmed balance for all methods of a given category.
        Includes only cleared amounts — uncleared cheques are excluded.
        """
        return self.balances.filter(
            payment_method__category__code=category_code,
            payment_method__clears_immediately=True
        ).aggregate(
            t=Coalesce(Sum('physical_closing_balance'), Decimal('0'))
        )['t']

    def cheques_in_transit(self) -> Decimal:
        """Uncleared bank instruments — real asset but not liquid."""
        return self.balances.filter(
            payment_method__clears_immediately=False
        ).aggregate(
            t=Coalesce(Sum('uncleared_amount'), Decimal('0'))
        )['t']


class SessionBalance(TimestampedModel):
    """
    One row per PaymentMethod per CashRegisterSession.
    To add Halopesa support: create a PaymentMethod record, run seed.
    This model needs zero changes.
    """
    session = models.ForeignKey(
        CashRegisterSession, on_delete=models.CASCADE, related_name='balances'
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT
    )
    physical_closing_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    system_expected_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    uncleared_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='For cheques only. Received but not yet cleared by bank.'
    )

    @property
    def cleared_balance(self) -> Decimal:
        return self.physical_closing_balance - self.uncleared_amount

    @property
    def variance_amount(self) -> Decimal:
        return self.system_expected_balance - self.cleared_balance

    class Meta:
        unique_together = [['session', 'payment_method']]
```

---

## PART 2 — REPORT PERIOD ENGINE

### 2.1 The Problem to Solve

Every report needs a date range. The user should never have to manually type `2026-05-01` to `2026-05-31` to get May's P&L. The system must offer:

- **Quick presets:** Today, Yesterday, This Week, Last Week, This Month, Last Month, This Quarter, Last Quarter, This Year
- **Manual date range:** From any date to any date
- **Report-appropriate defaults:** The income statement defaults to the current month. The debtor aging defaults to today (it's always a point-in-time snapshot). The stock report defaults to today.

This must be handled in one place — not reimplemented in every view.

### 2.2 The Period Engine — `apps/reports/periods.py`

```python
# apps/reports/periods.py
# NEW FILE — period resolution for all reports

from datetime import date, timedelta
from dataclasses import dataclass
from typing import Optional
import calendar


PRESET_CHOICES = [
    ('today',          'Today'),
    ('yesterday',      'Yesterday'),
    ('this_week',      'This Week'),
    ('last_week',      'Last Week'),
    ('this_month',     'This Month'),
    ('last_month',     'Last Month'),
    ('this_quarter',   'This Quarter'),
    ('last_quarter',   'Last Quarter'),
    ('this_year',      'This Year'),
    ('last_year',      'Last Year'),
    ('custom',         'Custom Range'),
]


@dataclass
class ReportPeriod:
    """
    Resolved period with start and end dates.
    Always constructed via ReportPeriod.resolve() — never directly.
    """
    start: date
    end: date
    preset: str          # the preset code, or 'custom'
    label: str           # human label for display in report header

    @classmethod
    def resolve(
        cls,
        preset: Optional[str] = None,
        start: Optional[date] = None,
        end: Optional[date] = None,
        default_preset: str = 'this_month',
        reference: Optional[date] = None,
    ) -> 'ReportPeriod':
        """
        Resolve a period from either a preset code or explicit start/end dates.

        Priority:
          1. If preset == 'custom' and start + end are both provided → use them
          2. If preset is a known code → compute start/end from that preset
          3. If neither → use default_preset

        Args:
            preset:         A PRESET_CHOICES code string
            start:          Explicit start date (only used when preset == 'custom')
            end:            Explicit end date (only used when preset == 'custom')
            default_preset: What to fall back to if nothing is provided
            reference:      'Today' for the calculation (defaults to date.today())
                            Useful in tests to freeze time.
        """
        today = reference or date.today()

        if preset == 'custom' and start and end:
            if start > end:
                start, end = end, start   # silently fix reversed dates
            return cls(start=start, end=end, preset='custom',
                       label=f'{start} → {end}')

        code = preset if preset in dict(PRESET_CHOICES) else default_preset

        s, e, label = cls._compute(code, today)
        return cls(start=s, end=e, preset=code, label=label)

    @staticmethod
    def _compute(code: str, today: date):
        """Return (start, end, label) for a given preset code."""
        # ── DAILY ────────────────────────────────────────────────
        if code == 'today':
            return today, today, f'Today ({today:%d %b %Y})'

        if code == 'yesterday':
            y = today - timedelta(days=1)
            return y, y, f'Yesterday ({y:%d %b %Y})'

        # ── WEEKLY ───────────────────────────────────────────────
        if code == 'this_week':
            # Monday to Sunday of current week
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            return monday, sunday, f'This Week ({monday:%d %b} – {sunday:%d %b %Y})'

        if code == 'last_week':
            monday = today - timedelta(days=today.weekday() + 7)
            sunday = monday + timedelta(days=6)
            return monday, sunday, f'Last Week ({monday:%d %b} – {sunday:%d %b %Y})'

        # ── MONTHLY ──────────────────────────────────────────────
        if code == 'this_month':
            s = today.replace(day=1)
            last = calendar.monthrange(today.year, today.month)[1]
            e = today.replace(day=last)
            return s, e, f'{today:%B %Y}'

        if code == 'last_month':
            first_of_this = today.replace(day=1)
            last_of_prev = first_of_this - timedelta(days=1)
            s = last_of_prev.replace(day=1)
            return s, last_of_prev, f'{last_of_prev:%B %Y}'

        # ── QUARTERLY ────────────────────────────────────────────
        if code == 'this_quarter':
            q = (today.month - 1) // 3 + 1
            q_start_month = (q - 1) * 3 + 1
            q_end_month = q_start_month + 2
            s = date(today.year, q_start_month, 1)
            last = calendar.monthrange(today.year, q_end_month)[1]
            e = date(today.year, q_end_month, last)
            return s, e, f'Q{q} {today.year}'

        if code == 'last_quarter':
            q = (today.month - 1) // 3 + 1
            last_q = q - 1 if q > 1 else 4
            last_q_year = today.year if q > 1 else today.year - 1
            q_start_month = (last_q - 1) * 3 + 1
            q_end_month = q_start_month + 2
            s = date(last_q_year, q_start_month, 1)
            last = calendar.monthrange(last_q_year, q_end_month)[1]
            e = date(last_q_year, q_end_month, last)
            return s, e, f'Q{last_q} {last_q_year}'

        # ── ANNUAL ───────────────────────────────────────────────
        if code == 'this_year':
            s = date(today.year, 1, 1)
            e = date(today.year, 12, 31)
            return s, e, f'Year {today.year}'

        if code == 'last_year':
            y = today.year - 1
            return date(y, 1, 1), date(y, 12, 31), f'Year {y}'

        # Fallback — should never reach here
        s = today.replace(day=1)
        last = calendar.monthrange(today.year, today.month)[1]
        e = today.replace(day=last)
        return s, e, f'{today:%B %Y}'

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def is_single_day(self) -> bool:
        return self.start == self.end

    @property
    def is_point_in_time(self) -> bool:
        """
        Some reports are snapshots at end date only (Balance Sheet, Debtor Aging,
        Stock Valuation). Use end date, not start date, for those.
        """
        return self.is_single_day

    def __str__(self):
        return self.label
```

### 2.3 The Period Form — Reusable Across All Report Views

```python
# apps/reports/forms.py

from django import forms
from datetime import date
from .periods import PRESET_CHOICES


class ReportPeriodForm(forms.Form):
    """
    Universal date range selector used by every report view.
    Renders as: [preset dropdown] [from date] [to date] [Run Report button]
    The from/to fields are shown/hidden via JS based on preset selection.
    """
    preset = forms.ChoiceField(
        choices=PRESET_CHOICES,
        initial='this_month',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'id_preset',
            'onchange': 'toggleCustomDates(this.value)',
        })
    )
    start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-sm',
            'id': 'id_start',
        })
    )
    end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-sm',
            'id': 'id_end',
        })
    )

    def clean(self):
        cleaned = super().clean()
        preset = cleaned.get('preset')
        start = cleaned.get('start')
        end = cleaned.get('end')

        if preset == 'custom':
            if not start:
                self.add_error('start', 'Start date is required for custom range.')
            if not end:
                self.add_error('end', 'End date is required for custom range.')
            if start and end and start > end:
                self.add_error('end', 'End date must be on or after start date.')
        return cleaned

    def resolved_period(self, default_preset='this_month'):
        """Call after is_valid(). Returns a ReportPeriod instance."""
        from .periods import ReportPeriod
        if not self.is_valid():
            return ReportPeriod.resolve(default_preset=default_preset)
        return ReportPeriod.resolve(
            preset=self.cleaned_data.get('preset'),
            start=self.cleaned_data.get('start'),
            end=self.cleaned_data.get('end'),
            default_preset=default_preset,
        )
```

### 2.4 The Period Selector Template Fragment

```html
{# templates/reports/_period_selector.html #}
{# Include this in every report template: {% include "reports/_period_selector.html" %} #}

<form method="get" class="row g-2 align-items-end mb-4 period-selector">

  <div class="col-auto">
    <label class="form-label small fw-semibold">Period</label>
    {{ form.preset }}
  </div>

  <div class="col-auto custom-dates" id="custom-date-fields"
       style="display: {% if form.preset.value == 'custom' %}flex{% else %}none{% endif %}; gap: 0.5rem;">
    <div>
      <label class="form-label small">From</label>
      {{ form.start }}
    </div>
    <div>
      <label class="form-label small">To</label>
      {{ form.end }}
    </div>
  </div>

  <div class="col-auto">
    <button type="submit" class="btn btn-primary btn-sm">
      <i class="bi bi-arrow-clockwise"></i> Run Report
    </button>
  </div>

  {% if period %}
  <div class="col-auto ms-auto">
    <span class="badge bg-secondary fs-6">{{ period.label }}</span>
    <a href="?{{ request.GET.urlencode }}&format=pdf" class="btn btn-outline-danger btn-sm ms-2">
      <i class="bi bi-file-pdf"></i> PDF
    </a>
  </div>
  {% endif %}

</form>

<script>
function toggleCustomDates(val) {
  document.getElementById('custom-date-fields').style.display =
    val === 'custom' ? 'flex' : 'none';
}
</script>
```

---

## PART 3 — REPORT TYPES & THEIR DJANGO IMPLEMENTATION

### 3.1 Report Classification

Every report falls into one of three types. The type determines how the view handles dates and what data it fetches.

```
TYPE 1 — FLOW REPORT      TYPE 2 — SNAPSHOT REPORT    TYPE 3 — OPERATIONAL REPORT
Uses: start + end date     Uses: end date only           Uses: no date (current state)
────────────────────────   ─────────────────────────     ──────────────────────────────
Income Statement (D1)      Balance Sheet (D2)            Low Stock Alert (A2)
Cash Flow (D3)             Debtor Aging (D5, C2)         Stock Valuation (E2)
Expense Analysis (D4)      Stock Valuation (point-in-    Live Sales Ticker (A1)
Sales Report (B2)          time variant)                 Cash Register Session
Liability Schedule (D6)
Drawings Summary (D7)
Purchase Summary (C3)
Budget vs Actual (F5)
```

**Why this matters in code:** A snapshot report ignores `start` entirely — it asks "what is the state *as of* the end date?" A flow report asks "what happened *between* start and end?" If you pass a full month range to a Balance Sheet calculation, you don't want the opening balance from start and closing from end — you want only the closing snapshot at end.

### 3.2 Base Report View — All Reports Inherit From This

```python
# apps/reports/views/base.py
# NEW FILE

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from ..forms import ReportPeriodForm
from ..periods import ReportPeriod


class BaseReportView(View):
    """
    Base class for every report view.

    Subclasses must define:
        template_name       — HTML template path
        pdf_template_name   — PDF template path (can be same as template_name)
        report_title        — string shown in header and PDF filename
        default_preset      — which period preset to default to
        report_type         — 'flow', 'snapshot', or 'operational'

    Subclasses must implement:
        get_context(period, request) → dict
            Returns all data the template needs, minus period/form (added here).
    """
    template_name = None
    pdf_template_name = None
    report_title = 'Report'
    default_preset = 'this_month'
    report_type = 'flow'        # 'flow' | 'snapshot' | 'operational'

    def get(self, request):
        form = ReportPeriodForm(request.GET or None)
        period = form.resolved_period(self.default_preset)

        ctx = self.get_context(period, request)
        ctx.update({
            'form': form,
            'period': period,
            'report_title': self.report_title,
            'shop_name': 'Upendo Stationery',
        })

        if request.GET.get('format') == 'pdf':
            return self._render_pdf(request, ctx)

        return render(request, self.template_name, ctx)

    def get_context(self, period: ReportPeriod, request) -> dict:
        raise NotImplementedError('Subclasses must implement get_context()')

    def _render_pdf(self, request, ctx):
        from weasyprint import HTML
        tpl = self.pdf_template_name or self.template_name
        html_string = render_to_string(tpl, ctx, request)
        pdf_bytes = HTML(
            string=html_string,
            base_url=request.build_absolute_uri()
        ).write_pdf()
        filename = (
            f"{self.report_title.lower().replace(' ', '_')}"
            f"_{ctx['period'].start}_{ctx['period'].end}.pdf"
        )
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
```

### 3.3 Every Report View — Full Implementation Map

```python
# apps/reports/views/income_statement.py

from .base import BaseReportView
from ..periods import ReportPeriod
from ..services.accounting import AccountingService
from apps.finance.services.expenses import ExpenseService


class IncomeStatementView(BaseReportView):
    template_name = 'reports/income_statement.html'
    report_title = 'Income Statement'
    default_preset = 'this_month'
    report_type = 'flow'

    def get_context(self, period: ReportPeriod, request) -> dict:
        svc = AccountingService(period.start, period.end)
        stmt = svc.to_income_statement()
        exp = ExpenseService(period.start, period.end)
        stmt['expenses'] = exp.by_type()
        stmt['total_expenses'] = exp.total()
        stmt['net_profit'] = stmt['gross_profit'] - stmt['total_expenses']
        return {'stmt': stmt}
```

```python
# apps/reports/views/balance_sheet.py

from .base import BaseReportView
from ..periods import ReportPeriod
from ..services.balance_sheet import BalanceSheetService


class BalanceSheetView(BaseReportView):
    template_name = 'reports/balance_sheet.html'
    report_title = 'Balance Sheet'
    default_preset = 'this_month'   # end date of month = snapshot date
    report_type = 'snapshot'        # uses period.end only

    def get_context(self, period: ReportPeriod, request) -> dict:
        # Snapshot report — only period.end matters
        svc = BalanceSheetService(as_of_date=period.end)
        return {'bs': svc.to_balance_sheet()}
```

```python
# apps/reports/views/debtor_aging.py

from .base import BaseReportView
from ..periods import ReportPeriod
from ..services.debtor_aging import debtor_aging_report


class DebtorAgingView(BaseReportView):
    template_name = 'reports/debtor_aging.html'
    report_title = 'Debtor Aging Report'
    default_preset = 'today'
    report_type = 'snapshot'

    def get_context(self, period: ReportPeriod, request) -> dict:
        # Snapshot — aging is always "as of" end date
        rows = debtor_aging_report(as_of=period.end)
        totals = {
            'current': sum(r['buckets']['current'] for r in rows),
            '1_30':    sum(r['buckets']['1_30']    for r in rows),
            '31_60':   sum(r['buckets']['31_60']   for r in rows),
            '61_90':   sum(r['buckets']['61_90']   for r in rows),
            '90_plus': sum(r['buckets']['90_plus'] for r in rows),
            'total':   sum(r['total']               for r in rows),
        }
        return {'rows': rows, 'totals': totals}
```

```python
# apps/reports/views/daily_sales.py

from .base import BaseReportView
from ..periods import ReportPeriod
from ..services.sales_summary import DailySalesSummaryService


class DailySalesView(BaseReportView):
    template_name = 'reports/daily_sales.html'
    report_title = 'Daily Sales Report'
    default_preset = 'today'
    report_type = 'flow'

    def get_context(self, period: ReportPeriod, request) -> dict:
        svc = DailySalesSummaryService(period.start, period.end)
        return {
            'by_method':  svc.by_payment_method(),
            'by_type':    svc.by_transaction_type(),
            'top_items':  svc.top_products(limit=10),
            'credit_detail': svc.credit_sales_detail(),
            'totals':     svc.totals(),
        }
```

```python
# apps/reports/views/stock_report.py

from .base import BaseReportView
from ..periods import ReportPeriod
from apps.catalog.models import ProductSpec
from django.db.models import F


class StockReportView(BaseReportView):
    template_name = 'reports/stock.html'
    report_title = 'Stock Valuation Report'
    default_preset = 'today'
    report_type = 'operational'   # always shows current state

    def get_context(self, period: ReportPeriod, request) -> dict:
        specs = ProductSpec.objects.select_related(
            'product', 'product__product_type', 'spec_value'
        ).order_by('product__name', 'spec_value__value')

        category_filter = request.GET.get('category')
        if category_filter:
            specs = specs.filter(
                product__product_type__category_id=category_filter
            )

        low_stock = specs.filter(current_stock__lte=F('reorder_level'))
        out_of_stock = specs.filter(current_stock__lte=0)
        total_value = sum(s.cached_stock_value for s in specs)

        return {
            'specs': specs,
            'low_stock_count': low_stock.count(),
            'out_of_stock_count': out_of_stock.count(),
            'total_stock_value': total_value,
        }
```

```python
# apps/reports/views/cash_reconciliation.py

from .base import BaseReportView
from ..periods import ReportPeriod
from apps.finance.models import CashRegisterSession


class CashReconciliationView(BaseReportView):
    template_name = 'reports/cash_reconciliation.html'
    report_title = 'Cash Reconciliation'
    default_preset = 'yesterday'   # you reconcile yesterday, not today (day is still open)
    report_type = 'snapshot'

    def get_context(self, period: ReportPeriod, request) -> dict:
        # For cash recon, always look at a single day — use end date
        try:
            session = CashRegisterSession.objects.prefetch_related(
                'balances__payment_method__category',
                'balances__payment_method__provider',
            ).get(session_date=period.end)
        except CashRegisterSession.DoesNotExist:
            session = None

        return {
            'session': session,
            'as_of': period.end,
        }
```

### 3.4 URL Structure — Reports App

```python
# apps/reports/urls.py — FULL REPLACEMENT

from django.urls import path
from .views import (
    income_statement, balance_sheet, cash_flow,
    debtor_aging, daily_sales, stock_report,
    expense_analysis, liability_schedule,
    drawings_summary, purchase_summary,
    cash_reconciliation, product_profitability,
    budget_vs_actual, low_stock,
)

app_name = 'reports'

urlpatterns = [
    # ── INDEX ────────────────────────────────────────────────────────
    path('', views.ReportIndexView.as_view(), name='index'),

    # ── INTRADAY / DAILY (Section A & B) ─────────────────────────────
    path('cash-reconciliation/',
         cash_reconciliation.CashReconciliationView.as_view(),
         name='cash-reconciliation'),

    path('daily-sales/',
         daily_sales.DailySalesView.as_view(),
         name='daily-sales'),

    path('low-stock/',
         low_stock.LowStockView.as_view(),
         name='low-stock'),

    # ── WEEKLY (Section C) ────────────────────────────────────────────
    path('debtor-aging/',
         debtor_aging.DebtorAgingView.as_view(),
         name='debtor-aging'),

    path('purchase-summary/',
         purchase_summary.PurchaseSummaryView.as_view(),
         name='purchase-summary'),

    # ── MONTHLY (Section D) ───────────────────────────────────────────
    path('income-statement/',
         income_statement.IncomeStatementView.as_view(),
         name='income-statement'),

    path('balance-sheet/',
         balance_sheet.BalanceSheetView.as_view(),
         name='balance-sheet'),

    path('cash-flow/',
         cash_flow.CashFlowView.as_view(),
         name='cash-flow'),

    path('expenses/',
         expense_analysis.ExpenseAnalysisView.as_view(),
         name='expenses'),

    path('liability-schedule/',
         liability_schedule.LiabilityScheduleView.as_view(),
         name='liability-schedule'),

    path('drawings/',
         drawings_summary.DrawingsSummaryView.as_view(),
         name='drawings'),

    # ── STOCK & PRODUCT ───────────────────────────────────────────────
    path('stock/',
         stock_report.StockReportView.as_view(),
         name='stock'),

    path('product-profitability/',
         product_profitability.ProductProfitabilityView.as_view(),
         name='product-profitability'),

    # ── ANNUAL (Section F) ────────────────────────────────────────────
    path('budget-vs-actual/',
         budget_vs_actual.BudgetVsActualView.as_view(),
         name='budget-vs-actual'),

    # ── SNAPSHOTS (locked periods) ────────────────────────────────────
    path('snapshots/',
         views.ReportSnapshotListView.as_view(),
         name='snapshot-list'),

    path('snapshots/<int:pk>/',
         views.ReportSnapshotDetailView.as_view(),
         name='snapshot-detail'),

    path('snapshots/<int:pk>/lock/',
         views.LockSnapshotView.as_view(),
         name='snapshot-lock'),
]
```

### 3.5 The Report Index View — One Screen, All Reports

```python
# apps/reports/views/index.py

from django.views.generic import TemplateView
from datetime import date


class ReportIndexView(TemplateView):
    template_name = 'reports/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()
        ctx['today'] = today

        # Quick links with pre-filled period params
        ctx['quick_links'] = [
            {
                'group': 'Daily',
                'reports': [
                    {
                        'title': "Today's Sales",
                        'url': '/reports/daily-sales/?preset=today',
                        'icon': 'bi-cart',
                        'color': 'primary',
                    },
                    {
                        'title': 'Cash Reconciliation',
                        'url': '/reports/cash-reconciliation/?preset=yesterday',
                        'icon': 'bi-cash-stack',
                        'color': 'success',
                    },
                    {
                        'title': 'Low Stock Alert',
                        'url': '/reports/low-stock/',
                        'icon': 'bi-exclamation-triangle',
                        'color': 'warning',
                    },
                ],
            },
            {
                'group': 'Monthly',
                'reports': [
                    {
                        'title': 'Income Statement',
                        'url': '/reports/income-statement/?preset=this_month',
                        'icon': 'bi-file-earmark-text',
                        'color': 'info',
                    },
                    {
                        'title': 'Balance Sheet',
                        'url': '/reports/balance-sheet/?preset=this_month',
                        'icon': 'bi-building',
                        'color': 'secondary',
                    },
                    {
                        'title': 'Expense Analysis',
                        'url': '/reports/expenses/?preset=this_month',
                        'icon': 'bi-receipt',
                        'color': 'danger',
                    },
                    {
                        'title': 'Debtor Aging',
                        'url': '/reports/debtor-aging/?preset=today',
                        'icon': 'bi-people',
                        'color': 'warning',
                    },
                ],
            },
            {
                'group': 'Stock & Products',
                'reports': [
                    {
                        'title': 'Stock Valuation',
                        'url': '/reports/stock/',
                        'icon': 'bi-boxes',
                        'color': 'primary',
                    },
                    {
                        'title': 'Product Profitability',
                        'url': '/reports/product-profitability/?preset=this_month',
                        'icon': 'bi-graph-up',
                        'color': 'success',
                    },
                ],
            },
        ]
        return ctx
```

---

## PART 4 — NEW SERVICES NEEDED

### 4.1 `DailySalesSummaryService` — feeds Report B2

```python
# apps/reports/services/sales_summary.py

from datetime import date
from decimal import Decimal
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from apps.sales.models import Sale
from apps.credit.models import Debt
from apps.sales.models import ReturnInward


class DailySalesSummaryService:
    """
    Produces all data for the Daily Sales Report (B2).
    Works for any date range — single day, week, month.
    """
    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end

    def _sales_qs(self):
        return Sale.objects.filter(sale_date__date__range=(self.start, self.end))

    def _debt_qs(self):
        return Debt.objects.filter(sale_date__date__range=(self.start, self.end))

    def by_payment_method(self) -> list:
        """Sales grouped by payment method — with category and provider."""
        return (
            self._sales_qs()
            .values(
                'payment_method__name',
                'payment_method__category__code',
                'payment_method__category__name',
                'payment_method__provider__name',
            )
            .annotate(
                count=Count('id'),
                total=Coalesce(Sum('amount'), Decimal('0')),
            )
            .order_by('payment_method__category__display_order', 'payment_method__name')
        )

    def by_transaction_type(self) -> dict:
        direct = self._sales_qs().aggregate(
            t=Coalesce(Sum('amount'), Decimal('0'))
        )['t']
        credit = self._debt_qs().aggregate(
            t=Coalesce(Sum('amount_due'), Decimal('0'))
        )['t']
        returns = ReturnInward.objects.filter(
            sale_date__date__range=(self.start, self.end)
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0')))['t']

        return {
            'direct_sales': direct,
            'credit_sales': credit,
            'return_inwards': returns,
            'gross_sales': direct + credit,
            'net_sales': direct + credit - returns,
        }

    def top_products(self, limit: int = 10) -> list:
        return (
            self._sales_qs()
            .values('product_spec__product__name', 'product_spec__spec_value__value')
            .annotate(
                units=Coalesce(Sum('quantity'), 0),
                revenue=Coalesce(Sum('amount'), Decimal('0')),
            )
            .order_by('-revenue')[:limit]
        )

    def credit_sales_detail(self) -> list:
        """Individual credit sales with debtor info — for the credit detail table."""
        return (
            self._debt_qs()
            .select_related('debtor', 'product_spec__product')
            .order_by('-sale_date')
        )

    def totals(self) -> dict:
        breakdown = self.by_transaction_type()
        return breakdown
```

### 4.2 `CashFlowService` — feeds Report D3

```python
# apps/reports/services/cash_flow.py

from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce
from .accounting import AccountingService
from .balance_sheet import BalanceSheetService
from apps.assets.models import Asset


class CashFlowService:
    """
    Indirect method Cash Flow Statement.
    Starts from net profit, adjusts for non-cash items and working capital changes.
    """
    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end
        self.acct = AccountingService(start, end)

    def net_profit(self) -> Decimal:
        from apps.finance.services.expenses import ExpenseService
        gp = self.acct.gross_profit()
        exp = ExpenseService(self.start, self.end).total()
        return gp - exp

    def depreciation_add_back(self) -> Decimal:
        """Depreciation is a non-cash expense — add back to get cash from operations."""
        assets = Asset.objects.filter(
            acquisition_date__lte=self.end,
            disposal_date__isnull=True
        )
        return sum(a.monthly_depreciation_charge * self._months() for a in assets)

    def _months(self) -> Decimal:
        """Approximate months in period."""
        return Decimal((self.end - self.start).days) / Decimal('30.44')

    def working_capital_changes(self) -> dict:
        """
        Changes in current assets/liabilities between start-1 and end.
        A rise in stock is a cash outflow. A rise in payables is a cash inflow.
        """
        from datetime import timedelta
        bs_open = BalanceSheetService(self.start - timedelta(days=1))
        bs_close = BalanceSheetService(self.end)

        stock_change = bs_close.inventory_value() - bs_open.inventory_value()
        receivables_change = bs_close.net_receivables() - bs_open.net_receivables()
        payables_change = bs_close.current_liabilities() - bs_open.current_liabilities()

        return {
            # Signs: increase in asset = cash outflow (negative), increase in liability = cash inflow (positive)
            'stock_change':       -stock_change,
            'receivables_change': -receivables_change,
            'payables_change':     payables_change,
        }

    def operating_cash_flow(self) -> Decimal:
        wc = self.working_capital_changes()
        return (
            self.net_profit()
            + self.depreciation_add_back()
            + wc['stock_change']
            + wc['receivables_change']
            + wc['payables_change']
        )

    def financing_cash_flow(self) -> dict:
        from apps.sales.models import Drawing
        from apps.finance.models import LiabilityPaymentDetail
        drawings = Drawing.objects.filter(
            sale_date__date__range=(self.start, self.end)
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0')))['t']

        principal_paid = LiabilityPaymentDetail.objects.filter(
            payment_date__date__range=(self.start, self.end)
        ).aggregate(t=Coalesce(Sum('principal_amount'), Decimal('0')))['t']

        return {
            'drawings': -drawings,
            'loan_repayment': -principal_paid,
            'total': -drawings - principal_paid,
        }

    def to_cash_flow(self) -> dict:
        wc = self.working_capital_changes()
        fin = self.financing_cash_flow()
        operating = self.operating_cash_flow()
        net = operating + fin['total']

        return {
            'period_start': self.start,
            'period_end': self.end,
            'net_profit': self.net_profit(),
            'depreciation': self.depreciation_add_back(),
            'stock_change': wc['stock_change'],
            'receivables_change': wc['receivables_change'],
            'payables_change': wc['payables_change'],
            'operating_cash_flow': operating,
            'drawings': fin['drawings'],
            'loan_repayment': fin['loan_repayment'],
            'financing_cash_flow': fin['total'],
            'investing_cash_flow': Decimal('0'),    # no investing activity tracked yet
            'net_cash_movement': net,
        }
```

---

## PART 5 — REPORT SNAPSHOT IMPLEMENTATION

### 5.1 When to Snapshot

Not every report should be snapshotted. Only reports where the data could change retroactively need locking.

```
SNAPSHOT THESE:                         DO NOT SNAPSHOT:
Monthly Income Statement (D1)           Low Stock Alert (A2)      — always live
Monthly Balance Sheet (D2)              Daily Sales (B2)          — operational view
Monthly Cash Flow (D3)                  Debtor Aging (D5)         — always run fresh
Monthly Expense Analysis (D4)           Stock Report              — always live
Monthly Debtor Aging — formal (D5)      Product Profitability     — always run fresh
Quarterly Management Pack (E1)
Annual P&L and Balance Sheet
```

### 5.2 Snapshot View — Lock Button Flow

```python
# apps/reports/views/snapshots.py

from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from ..models import ReportSnapshot
from ..services.accounting import AccountingService
from ..services.balance_sheet import BalanceSheetService
import json


class LockSnapshotView(View):
    """
    POST only. Locks a report snapshot.
    Called when the owner clicks 'Sign Off This Month'.
    """
    def post(self, request, pk):
        snapshot = get_object_or_404(ReportSnapshot, pk=pk)
        if snapshot.is_locked:
            messages.warning(request, 'This report is already locked.')
            return redirect('reports:snapshot-detail', pk=pk)

        locked_by = request.POST.get('locked_by', 'Owner')
        snapshot.lock(locked_by)
        messages.success(
            request,
            f'Report locked and signed off by {locked_by}. '
            'This period\'s figures are now frozen.'
        )
        return redirect('reports:snapshot-detail', pk=pk)


def generate_and_save_snapshot(report_code: str, period_start, period_end,
                                generated_by: str = 'System') -> ReportSnapshot:
    """
    Generate a report snapshot for a given period.
    Call this at month-end or when the owner clicks 'Generate Report'.
    """
    from ..services.accounting import AccountingService
    from ..services.balance_sheet import BalanceSheetService
    from apps.finance.services.expenses import ExpenseService

    if report_code == 'D1':
        svc = AccountingService(period_start, period_end)
        data = svc.to_income_statement()
        exp = ExpenseService(period_start, period_end)
        data['expenses'] = list(exp.by_type().values('name', 'total'))
        data['total_expenses'] = float(exp.total())
        data['net_profit'] = float(data['gross_profit'] - exp.total())

    elif report_code == 'D2':
        svc = BalanceSheetService(period_end)
        data = svc.to_balance_sheet()

    else:
        raise ValueError(f'Snapshot generation not implemented for {report_code}')

    snapshot, created = ReportSnapshot.objects.update_or_create(
        report_code=report_code,
        period_start=period_start,
        period_end=period_end,
        defaults={
            'generated_by': generated_by,
            'is_locked': False,
            'data': data,
        }
    )
    return snapshot
```

---

## PART 6 — MIGRATION SEQUENCE & FILE STRUCTURE

### 6.1 New Files to Create (in order)

```
apps/
├── core/
│   ├── __init__.py
│   └── models.py                     ← TimestampedModel abstract base

├── finance/
│   └── management/
│       └── commands/
│           └── seed_payment_methods.py   ← NEW

├── reports/
│   ├── periods.py                    ← NEW — ReportPeriod engine
│   ├── forms.py                      ← NEW — ReportPeriodForm
│   ├── models.py                     ← NEW — ReportSnapshot
│   │
│   ├── views/
│   │   ├── __init__.py
│   │   ├── base.py                   ← NEW — BaseReportView
│   │   ├── index.py                  ← NEW
│   │   ├── income_statement.py       ← REPLACES existing view
│   │   ├── balance_sheet.py          ← NEW
│   │   ├── cash_flow.py              ← NEW
│   │   ├── debtor_aging.py           ← REPLACES existing
│   │   ├── daily_sales.py            ← NEW
│   │   ├── stock_report.py           ← REPLACES existing
│   │   ├── expense_analysis.py       ← NEW
│   │   ├── liability_schedule.py     ← NEW
│   │   ├── drawings_summary.py       ← NEW
│   │   ├── purchase_summary.py       ← NEW
│   │   ├── cash_reconciliation.py    ← NEW
│   │   ├── product_profitability.py  ← NEW
│   │   ├── budget_vs_actual.py       ← NEW
│   │   ├── low_stock.py              ← REPLACES existing
│   │   └── snapshots.py              ← NEW
│   │
│   └── services/
│       ├── accounting.py             ← EXISTS — minor modifications
│       ├── balance_sheet.py          ← NEW
│       ├── cash_flow.py              ← NEW
│       ├── sales_summary.py          ← NEW
│       ├── debtor_aging.py           ← EXISTS — no changes needed
│       └── expenses.py               ← EXISTS — no changes needed

templates/
└── reports/
    ├── index.html                    ← NEW
    ├── _period_selector.html         ← NEW — shared fragment
    ├── income_statement.html         ← EXISTS — add period selector
    ├── balance_sheet.html            ← NEW
    ├── cash_flow.html                ← NEW
    ├── debtor_aging.html             ← EXISTS — add period selector
    ├── daily_sales.html              ← NEW
    ├── stock.html                    ← EXISTS — update
    ├── expense_analysis.html         ← NEW
    ├── liability_schedule.html       ← NEW
    ├── drawings_summary.html         ← NEW
    ├── purchase_summary.html         ← NEW
    ├── cash_reconciliation.html      ← NEW
    ├── product_profitability.html    ← NEW
    ├── budget_vs_actual.html         ← NEW
    └── snapshot_list.html            ← NEW
```

### 6.2 Migration Order

```bash
# Step 1 — core app (TimestampedModel — no migrations needed, it's abstract)
python manage.py startapp core apps/core

# Step 2 — model field additions
python manage.py makemigrations finance   # PaymentCategory, PaymentProvider, updated PaymentMethod
python manage.py makemigrations finance   # BudgetLine, CashRegisterSession, SessionBalance
python manage.py makemigrations catalog  # ProductSpec: cached_wac, cached_stock_value
python manage.py makemigrations inventory # Purchase: carriage_inwards
python manage.py makemigrations sales    # Sale: reference_number; Drawing: drawing_type, cash_amount
python manage.py makemigrations credit   # Debt: reference_number; Debtor: credit_limit, is_blocked
python manage.py makemigrations assets   # Asset: full depreciation fields
python manage.py makemigrations reports  # ReportSnapshot

# Step 3 — run
python manage.py migrate

# Step 4 — seed
python manage.py seed_payment_methods

# Step 5 — backfill WAC cache
python manage.py shell -c "
from apps.catalog.models import ProductSpec
for s in ProductSpec.objects.all():
    s.refresh_wac()
print(f'WAC refreshed for {ProductSpec.objects.count()} specs.')
"

# Step 6 — backfill asset references
python manage.py shell -c "
from apps.assets.models import Asset
for a in Asset.objects.all():
    if not a.asset_reference:
        a.asset_reference = f'FA-{a.pk:03d}'
        a.save(update_fields=['asset_reference'])
print('Asset references backfilled.')
"

# Step 7 — verify integrity
python manage.py verify_accounting_integrity
```

### 6.3 Build Priority Order

This is the sequence to follow when building. Each step is a working deliverable.

```
PHASE 1 — Foundation (do this first, nothing else works without it)
  ├── PaymentCategory + PaymentProvider + PaymentMethod (new structure)
  ├── seed_payment_methods command
  ├── periods.py (ReportPeriod engine)
  ├── forms.py (ReportPeriodForm)
  ├── _period_selector.html template fragment
  └── BaseReportView

PHASE 2 — Core Daily Operations
  ├── CashRegisterSession + SessionBalance models
  ├── DailySalesView + template
  ├── CashReconciliationView + template
  └── LowStockView + template

PHASE 3 — Monthly Management Reports
  ├── IncomeStatementView (refactored onto BaseReportView)
  ├── BalanceSheetService + BalanceSheetView + template
  ├── CashFlowService + CashFlowView + template
  ├── ExpenseAnalysisView + template
  └── DebtorAgingView (refactored onto BaseReportView)

PHASE 4 — Stock & Product Reports
  ├── ProductSpec.cached_wac + refresh_wac()
  ├── StockReportView (refactored)
  └── ProductProfitabilityView + template

PHASE 5 — Period Locking
  ├── ReportSnapshot model
  ├── generate_and_save_snapshot()
  ├── LockSnapshotView
  └── snapshot_list.html + snapshot_detail.html

PHASE 6 — Annual & Budget
  ├── BudgetLine model + BudgetVsActualView
  └── Annual summary views (reuse monthly services with full-year period)
```

---

## PART 7 — TESTING THE REPORTS SYSTEM

### 7.1 Test the Period Engine First — It Has No Dependencies

```python
# apps/reports/tests/test_periods.py

from datetime import date
from django.test import TestCase
from ..periods import ReportPeriod


class TestReportPeriod(TestCase):

    def test_this_month_start_is_first_of_month(self):
        p = ReportPeriod.resolve('this_month', reference=date(2026, 5, 15))
        self.assertEqual(p.start, date(2026, 5, 1))
        self.assertEqual(p.end, date(2026, 5, 31))

    def test_last_month(self):
        p = ReportPeriod.resolve('last_month', reference=date(2026, 5, 15))
        self.assertEqual(p.start, date(2026, 4, 1))
        self.assertEqual(p.end, date(2026, 4, 30))

    def test_this_quarter_q2(self):
        p = ReportPeriod.resolve('this_quarter', reference=date(2026, 5, 15))
        self.assertEqual(p.start, date(2026, 4, 1))
        self.assertEqual(p.end, date(2026, 6, 30))

    def test_last_quarter_from_q1(self):
        p = ReportPeriod.resolve('last_quarter', reference=date(2026, 2, 1))
        self.assertEqual(p.start, date(2025, 10, 1))
        self.assertEqual(p.end, date(2025, 12, 31))

    def test_custom_range(self):
        p = ReportPeriod.resolve(
            'custom',
            start=date(2026, 3, 15),
            end=date(2026, 4, 20)
        )
        self.assertEqual(p.start, date(2026, 3, 15))
        self.assertEqual(p.end, date(2026, 4, 20))
        self.assertEqual(p.preset, 'custom')

    def test_reversed_custom_dates_are_corrected(self):
        # If user picks end before start, silently fix it
        p = ReportPeriod.resolve(
            'custom',
            start=date(2026, 5, 31),
            end=date(2026, 5, 1)
        )
        self.assertEqual(p.start, date(2026, 5, 1))
        self.assertEqual(p.end, date(2026, 5, 31))

    def test_invalid_preset_falls_back_to_default(self):
        p = ReportPeriod.resolve('nonsense', default_preset='this_month',
                                  reference=date(2026, 5, 15))
        self.assertEqual(p.start, date(2026, 5, 1))

    def test_today(self):
        today = date.today()
        p = ReportPeriod.resolve('today')
        self.assertEqual(p.start, today)
        self.assertEqual(p.end, today)
        self.assertTrue(p.is_single_day)

    def test_this_week(self):
        # 2026-05-04 is a Monday
        p = ReportPeriod.resolve('this_week', reference=date(2026, 5, 6))
        self.assertEqual(p.start.weekday(), 0)  # Monday
        self.assertEqual(p.end.weekday(), 6)    # Sunday
```

### 7.2 Test Payment Method Filtering — Category Code Never Breaks

```python
# apps/finance/tests/test_payment_methods.py

from django.test import TestCase
from apps.finance.models import PaymentCategory, PaymentProvider, PaymentMethod
from django.core.management import call_command


class TestPaymentMethodStructure(TestCase):

    def setUp(self):
        call_command('seed_payment_methods', verbosity=0)

    def test_all_methods_have_a_category(self):
        for method in PaymentMethod.objects.all():
            self.assertIsNotNone(method.category)

    def test_cash_has_no_provider(self):
        cash = PaymentMethod.objects.get(name='Cash')
        self.assertIsNone(cash.provider)
        self.assertTrue(cash.is_cash)
        self.assertTrue(cash.clears_immediately)

    def test_mpesa_is_mobile_money(self):
        mpesa = PaymentMethod.objects.get(name='M-Pesa')
        self.assertTrue(mpesa.is_mobile_money)
        self.assertTrue(mpesa.clears_immediately)
        self.assertEqual(mpesa.provider.name, 'Vodacom')

    def test_cheques_do_not_clear_immediately(self):
        cheques = PaymentMethod.objects.filter(
            clears_immediately=False
        )
        self.assertTrue(cheques.exists())
        for c in cheques:
            self.assertIn('Cheque', c.name)
            self.assertTrue(c.is_bank)

    def test_mobile_money_filter_by_category_code(self):
        mobile = PaymentMethod.objects.filter(
            category__code='MOBILE_MONEY'
        )
        names = list(mobile.values_list('name', flat=True))
        self.assertIn('M-Pesa', names)
        self.assertIn('Tigo Pesa', names)
        self.assertIn('Airtel Money', names)
        # New providers added later will also appear here — no code changes needed

    def test_adding_new_provider_requires_no_code_change(self):
        # Simulate adding a new hypothetical provider
        cat = PaymentCategory.objects.get(code='MOBILE_MONEY')
        prov = PaymentProvider.objects.create(name='HaloTel', category=cat)
        PaymentMethod.objects.create(
            name='HaloTel Money', category=cat, provider=prov,
            clears_immediately=True
        )
        # Existing filter still works — picks up the new method automatically
        count = PaymentMethod.objects.filter(category__code='MOBILE_MONEY').count()
        self.assertGreaterEqual(count, 5)   # original 4 + new 1
```

---

## PART 8 — COMMON MISTAKES TO AVOID

```
MISTAKE                                  CORRECT APPROACH
────────────────────────────────────────────────────────────────────────────
Filtering by payment_method__name        Filter by category__code
Hardcoding 'M-Pesa' in any view/service  Always use category code lookup
Using FloatField for money               Always DecimalField(max_digits=15, decimal_places=2)
Storing month_id or month_name           Derive with TruncMonth / ExtractMonth
Calling AccountingService per product    Aggregate with spec_id=None for totals
Building period logic inside each view   Use ReportPeriod.resolve() always
Forgetting clears_immediately on cheques Show cheques in transit separately — not in cash balance
Running snapshot generation in a view    Move to management command or Celery task
Not calling refresh_wac() after delete   Override PurchaseDetail.delete() to trigger it
Two date fields on the same model        One canonical date field per model — no exceptions
```

---

*Document: Kiyabo Duka — Programmer's Implementation Guide*
*Version: 1.0 — May 2026*
*Covers: PaymentMethod architecture · Period Engine · Report views · Services · Testing*
*Stack: Django 5.x · PostgreSQL 16 · WeasyPrint · Bootstrap 5*
*Shop: Upendo Stationery, Dar es Salaam, Tanzania*
