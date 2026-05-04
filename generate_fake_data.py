"""
Fake data generator for Kiyabo Duka — Jan 2026 to May 2026.

Covers: Purchases, Sales, ReturnInward, ReturnOutward, Drawings,
        Debts (credit sales), DebtReturns, Expense Payments,
        Liability Payments, CashRegisterSessions, SaleOfficeUse.

Run:
    /root/apis/duka-letu/venv/bin/python3 generate_fake_data.py
"""

import os, sys, shutil, django, random, calendar
from decimal import Decimal
from datetime import date, datetime, timedelta
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kiyabo_duka.settings')
sys.path.insert(0, '/root/apis/duka-letu')
django.setup()

# ── backup SQLite before touching anything ────────────────────────────────────
_DB = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
_BACKUP = _DB + '.bak_' + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(_DB, _BACKUP)
print(f"Backup created: {_BACKUP}")
# ─────────────────────────────────────────────────────────────────────────────

from django.db.models import F, Sum, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware
from catalog.models import ProductSpec
from inventory.models import Supplier, Purchase, PurchaseDetail, ReturnOutward
from sales.models import Sale, ReturnInward, Drawing, DrawingCategory, SaleOfficeUse, OfficeUseCategory
from credit.models import Debtor, Debt, DebtReturn
from finance.models import (
    PaymentMethod, PaymentObligation, Payment, LiabilityItem,
    LiabilityPaymentDetail, CashRegisterSession, SessionBalance
)

EAT = pytz.timezone('Africa/Dar_es_Salaam')
CASH_PM = PaymentMethod.objects.get(pk=1)   # Cash
BANK_PM  = PaymentMethod.objects.get(pk=2)  # Bank (Cheque)

random.seed(42)

# ── helpers ───────────────────────────────────────────────────────────────────

def dt(d: date, hour=9, minute=0) -> datetime:
    """Return timezone-aware datetime for EAT."""
    return EAT.localize(datetime(d.year, d.month, d.day, hour, minute))


def rand_time(d: date) -> datetime:
    h = random.randint(8, 17)
    m = random.randint(0, 59)
    return dt(d, h, m)


def selling_price(spec: ProductSpec) -> Decimal:
    """WAC * markup 1.5–2.0x, rounded to nearest 100, minimum WAC+100."""
    wac = spec.cached_wac
    if wac > 0:
        markup = Decimal(str(round(random.uniform(1.5, 2.0), 2)))
        rounded = round(float(wac * markup) / 100) * 100
        return Decimal(str(max(rounded, float(wac) + 100)))
    if getattr(spec, 'default_selling_price', None):
        return spec.default_selling_price
    return Decimal('500')


def sale_qty(spec: ProductSpec) -> int:
    """
    Realistic qty per sale based on WAC tier — from real 2025 data:
      ≤100 TZS  (pens, pencils, envelopes):  5–20 units
      101–500   (glue, staple pins, bags):    3–15 units
      501–2000  (daftari, shorthand, books):  1–8  units
      2001–5000 (K-Series, counter books):    1–4  units
      5000+     (K-100, photocopy paper):     1–2  units
    """
    wac = float(spec.cached_wac)
    if wac <= 100:    qty = random.randint(5, 20)
    elif wac <= 500:  qty = random.randint(3, 15)
    elif wac <= 2000: qty = random.randint(1, 8)
    elif wac <= 5000: qty = random.randint(1, 4)
    else:             qty = random.randint(1, 2)
    return min(qty, spec.current_stock)


def workdays(year: int, month: int) -> list[date]:
    """Return Mon–Sat dates for a month (shop closed Sundays)."""
    days = []
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        d = date(year, month, day)
        if d.weekday() != 6:  # not Sunday
            days.append(d)
    return days


def active_specs() -> list[ProductSpec]:
    """
    Product specs with stock > 0 and either:
      - a cached WAC > 0, OR
      - a default_selling_price set (WAC not yet calculated but price is known).
    """
    return list(
        ProductSpec.objects.filter(current_stock__gt=0)
        .filter(Q(cached_wac__gt=0) | Q(default_selling_price__gt=0))
    )


# ── 1. PURCHASES ──────────────────────────────────────────────────────────────

def make_purchases():
    """
    Jan–May 2026: 3–5 purchases/month restocking low-stock items.
    Each purchase has 2–5 line items.
    """
    print("\n=== PURCHASES ===")
    suppliers = list(Supplier.objects.all())

    # Products to restock: those with stock < 30 and WAC > 0
    restock_specs = list(ProductSpec.objects.filter(cached_wac__gt=0).order_by('current_stock'))

    months = [
        (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5),
    ]

    for year, month in months:
        days = workdays(year, month)
        n_purchases = random.randint(3, 5)
        purchase_days = sorted(random.sample(days[:20], min(n_purchases, len(days[:20]))))

        for pday in purchase_days:
            supplier = random.choice(suppliers)
            purchase = Purchase.objects.create(
                supplier=supplier,
                purchase_date=dt(pday, random.randint(9, 14)),
                invoice_number=str(random.randint(100000, 999999)) if random.random() > 0.4 else '',
                carriage_inwards=Decimal(str(random.choice([0, 0, 0, 2000, 3000, 5000]))),
            )

            # Pick 2–5 specs to restock
            n_items = random.randint(2, 5)
            chosen = random.sample(restock_specs[:40], min(n_items, len(restock_specs[:40])))
            for spec in chosen:
                qty = random.randint(150, 400)
                PurchaseDetail.objects.create(
                    purchase=purchase,
                    product_spec=spec,
                    quantity=qty,
                    unit_cost=spec.cached_wac,
                )
            print(f"  Purchase#{purchase.pk} {pday} {supplier.name} ({len(chosen)} items)")


# ── 2. SALES ──────────────────────────────────────────────────────────────────

def make_sales():
    """
    Jan–May 2026: ~200–350 sales/month, mostly Cash.
    Prices = WAC * 1.5–2x. Qty 1–10 per line.
    """
    print("\n=== SALES ===")
    months = [
        (2026, 1, 280), (2026, 2, 320), (2026, 3, 200),
        (2026, 4, 300), (2026, 5, 180),  # May up to today (3rd)
    ]

    for year, month, target in months:
        days = workdays(year, month)
        # For May 2026 only go up to the 3rd
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]
            target = 15  # only 3 days

        specs = active_specs()
        if not specs:
            print(f"  {year}-{month:02d}: no active specs, skipping")
            continue

        # Distribute sales across days
        sales_per_day = max(1, target // len(days))
        created = 0

        for d in days:
            n = random.randint(max(1, sales_per_day - 3), sales_per_day + 5)
            for _ in range(n):
                if not specs:
                    specs = active_specs()
                if not specs:
                    break
                spec = random.choice(specs)
                if spec.current_stock <= 0:
                    specs = [s for s in specs if s.pk != spec.pk]
                    continue
                qty = sale_qty(spec)
                if qty <= 0:
                    continue
                price = selling_price(spec)
                pm = CASH_PM if random.random() < 0.98 else BANK_PM

                Sale.objects.create(
                    product_spec=spec,
                    quantity=qty,
                    unit_price=price,
                    discount=Decimal('0'),
                    sale_date=rand_time(d),
                    payment_method=pm,
                )
                created += 1
                # Refresh spec stock
                spec.refresh_from_db()
                if spec.current_stock <= 0:
                    specs = [s for s in specs if s.pk != spec.pk]

        print(f"  {year}-{month:02d}: {created} sales created")


# ── 3. RETURN INWARD ──────────────────────────────────────────────────────────

def make_return_inward():
    """2–3 customer returns per month."""
    print("\n=== RETURN INWARD ===")
    months = [(2026, m) for m in range(1, 6)]

    for year, month in months:
        days = workdays(year, month)
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]

        # Pick recent sales from this month to return
        month_start = make_aware(datetime(year, month, 1), EAT)
        month_end = make_aware(datetime(year, month, 28), EAT)
        sales_this_month = list(
            Sale.objects.filter(sale_date__gte=month_start, sale_date__lte=month_end)
                        .order_by('?')[:5]
        )

        n = random.randint(1, 3)
        for sale in sales_this_month[:n]:
            ret_qty = 1
            ret_day = random.choice(days[-5:]) if days else date(year, month, 15)
            ReturnInward.objects.create(
                sale=sale,
                quantity=ret_qty,
                unit_price=sale.unit_price,
                reason=random.choice(['Damaged', 'Wrong item', 'Customer changed mind', 'Defective']),
                sale_date=rand_time(ret_day),
            )
            print(f"  ReturnInward: Sale#{sale.pk} qty={ret_qty} on {ret_day}")


# ── 4. RETURN OUTWARD ─────────────────────────────────────────────────────────

def make_return_outward():
    """1–2 supplier returns total across the period."""
    print("\n=== RETURN OUTWARD ===")
    # Pick a purchase detail from Jan 2026 onwards
    jan_start = make_aware(datetime(2026, 1, 1), EAT)
    details = list(
        PurchaseDetail.objects.filter(purchase__purchase_date__gte=jan_start)
                              .order_by('?')[:3]
    )
    for detail in details[:2]:
        ret_date = detail.purchase.purchase_date.date() + timedelta(days=random.randint(3, 10))
        # Cap return qty to what was purchased (stock may have moved since)
        ret_qty = random.randint(1, min(3, detail.quantity))
        ReturnOutward.objects.create(
            purchase_detail=detail,
            quantity=ret_qty,
            unit_price=detail.unit_cost,
            reason=random.choice(['Damaged on delivery', 'Wrong specification', 'Excess stock']),
            sale_date=dt(ret_date, 10),
        )
        print(f"  ReturnOutward: PurchaseDetail#{detail.pk} qty={ret_qty} on {ret_date}")


# ── 5. DRAWINGS ───────────────────────────────────────────────────────────────

def make_drawings():
    """2–3 cash drawings per month (owner withdrawals)."""
    print("\n=== DRAWINGS ===")
    cat, _ = DrawingCategory.objects.get_or_create(name='Personal Use')
    months = [(2026, m) for m in range(1, 6)]

    for year, month in months:
        days = workdays(year, month)
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]
        if not days:
            continue

        n = random.randint(2, 3)
        draw_days = random.sample(days, min(n, len(days)))
        for d in draw_days:
            amount = Decimal(str(random.choice([50000, 100000, 150000, 200000, 300000])))
            Drawing.objects.create(
                drawing_category=cat,
                drawing_type='CASH',
                cash_amount=amount,
                sale_date=rand_time(d),
                notes='Owner withdrawal',
            )
            print(f"  Drawing CASH TZS {amount:,.0f} on {d}")


# ── 6. CREDIT SALES (DEBTS) ───────────────────────────────────────────────────

def make_debts():
    """5–8 new credit sales per month."""
    print("\n=== CREDIT SALES (DEBTS) ===")
    debtors = list(Debtor.objects.all())
    months = [(2026, m) for m in range(1, 6)]

    for year, month in months:
        days = workdays(year, month)
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]
        if not days:
            continue

        specs = active_specs()
        n = random.randint(3, 6) if month == 5 else random.randint(5, 8)
        debt_days = random.sample(days, min(n, len(days)))

        for d in debt_days:
            debtor = random.choice(debtors)
            if not specs:
                specs = active_specs()
            if not specs:
                break
            spec = random.choice(specs)
            spec.refresh_from_db()
            if spec.current_stock <= 0:
                specs = [s for s in specs if s.pk != spec.pk]
                continue
            qty = sale_qty(spec)
            if qty <= 0:
                continue
            price = selling_price(spec)
            due = d + timedelta(days=random.randint(14, 45))

            debt = Debt.objects.create(
                debtor=debtor,
                product_spec=spec,
                quantity=qty,
                unit_price=price,
                discount=Decimal('0'),
                sale_date=rand_time(d),
                expected_payment_date=due,
                payment_method=CASH_PM,
            )
            print(f"  Debt#{debt.pk}: {debtor.name} | {spec} qty={qty} TZS {price} due={due}")
            spec.refresh_from_db()


# ── 7. DEBT RETURNS (REPAYMENTS) ──────────────────────────────────────────────

def make_debt_returns():
    """
    Partial repayments on existing debts.
    - Clear Matola Joackim (93 TZS balance)
    - Partial payments on others
    """
    print("\n=== DEBT REPAYMENTS ===")
    months = [(2026, m) for m in range(1, 6)]

    for year, month in months:
        days = workdays(year, month)
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]
        if not days:
            continue

        # Find debts with outstanding balance
        outstanding = list(Debt.objects.all())
        outstanding = [d for d in outstanding if d.balance > 0]

        n = random.randint(2, 5)
        for debt in random.sample(outstanding, min(n, len(outstanding))):
            pay_day = random.choice(days)
            # Pay partial or full
            pay_amount = min(debt.balance, Decimal(str(random.choice([
                1000, 2000, 3000, 5000, 10000, 15000, 20000
            ]))))
            if pay_amount <= 0:
                continue
            DebtReturn.objects.create(
                debt=debt,
                amount=pay_amount,
                return_date=rand_time(pay_day),
                payment_method=CASH_PM,
                comment=f'Partial payment {year}-{month:02d}',
            )
            print(f"  DebtReturn: {debt.debtor.name} Debt#{debt.pk} TZS {pay_amount:,.0f} on {pay_day}")


# ── 8. EXPENSE PAYMENTS ───────────────────────────────────────────────────────

def make_expense_payments():
    """
    Directly create one obligation per expense item per month (Jan–May 2026)
    then pay it in the first week of that month.
    Skips items with rate=0 (variable expenses with no set amount).
    """
    print("\n=== EXPENSE PAYMENTS ===")
    from finance.models import ExpenseItem
    months = [(2026, m) for m in range(1, 6)]

    for year, month in months:
        days = workdays(year, month)
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]
        if not days:
            continue
        pay_day = days[random.randint(0, min(4, len(days) - 1))]
        due_day = date(year, month, calendar.monthrange(year, month)[1])  # last day of month

        for item in ExpenseItem.objects.filter(is_active=True):
            rate = item.current_rate()
            if rate <= 0:
                continue  # skip variable-rate items (Umeme, Matangazo, etc.)

            # Idempotent: skip if obligation already exists for this item+month
            already = PaymentObligation.objects.filter(
                expense_item=item,
                obligation_type='EXPENSE',
                due_date__year=year,
                due_date__month=month,
            ).exists()
            if already:
                continue

            ob = PaymentObligation.objects.create(
                expense_item=item,
                obligation_type='EXPENSE',
                obligation_date=date(year, month, 1),
                due_date=due_day,
                amount_due=rate,
                description=f'{item.name} — {year}/{month:02d}',
            )
            payment = Payment.objects.create(
                obligation=ob,
                expense_item=item,
                payment_type='EXPENSE',
                payment_date=rand_time(pay_day),
                amount_paid=rate,
                payment_method=CASH_PM,
                description=f'Payment: {item.name} {year}/{month:02d}',
            )
            ob.amount_paid = rate
            ob.save(update_fields=['amount_paid'])
            print(f"  {pay_day} {item} TZS {rate:,.0f}")


# ── 9. LIABILITY PAYMENTS ─────────────────────────────────────────────────────

def make_liability_payments():
    """
    2 NMB loan payments across the period (principal only, no interest rate set).
    """
    print("\n=== LIABILITY PAYMENTS ===")
    liability = LiabilityItem.objects.get(pk=1)  # NMB Business Loan
    payment_dates = [date(2026, 2, 15), date(2026, 4, 15)]
    principal_each = Decimal('80000')

    for pdate in payment_dates:
        # Skip if a liability payment already exists on this date
        already = Payment.objects.filter(
            liability_item=liability,
            payment_type='LIABILITY',
            payment_date__date=pdate,
        ).exists()
        if already:
            print(f"  Skipping {pdate} — already paid")
            continue
        liability.refresh_from_db()
        balance_before = liability.current_balance
        payment = Payment.objects.create(
            liability_item=liability,
            payment_type='LIABILITY',
            payment_date=dt(pdate, 10),
            amount_paid=principal_each,
            payment_method=BANK_PM,
            description='NMB Business Loan instalment',
        )
        LiabilityPaymentDetail.objects.create(
            payment=payment,
            liability_item=liability,
            principal_amount=principal_each,
            interest_amount=Decimal('0'),
            balance_after_payment=balance_before - principal_each,
            payment_date=dt(pdate, 10),
        )
        print(f"  LiabilityPayment#{payment.pk}: TZS {principal_each:,.0f} on {pdate}")


# ── 10. CASH REGISTER SESSIONS ────────────────────────────────────────────────

def make_cash_sessions():
    """
    Create CashRegisterSession for each active sales day.
    """
    print("\n=== CASH REGISTER SESSIONS ===")
    months = [(2026, m) for m in range(1, 6)]

    for year, month in months:
        days = workdays(year, month)
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]

        # Only create sessions for days that have sales
        for d in days:
            day_start = make_aware(datetime(d.year, d.month, d.day, 0, 0), EAT)
            day_end = make_aware(datetime(d.year, d.month, d.day, 23, 59), EAT)
            has_sales = Sale.objects.filter(sale_date__gte=day_start, sale_date__lte=day_end).exists()
            if not has_sales:
                continue

            if CashRegisterSession.objects.filter(session_date=d).exists():
                continue

            # Calculate expected cash from sales
            expr = ExpressionWrapper(F('quantity')*F('unit_price')-F('discount'), output_field=DecimalField(max_digits=15,decimal_places=2))
            cash_sales = Sale.objects.filter(
                sale_date__gte=day_start, sale_date__lte=day_end,
                payment_method=CASH_PM
            ).aggregate(t=Sum(expr))['t'] or Decimal('0')

            opening = Decimal('50000')  # standard float
            session = CashRegisterSession.objects.create(
                session_date=d,
                opened_by='Juma Kinyogoli',
                closed_by='Juma Kinyogoli',
                opening_float=opening,
                status='CLOSED',
            )
            SessionBalance.objects.create(
                session=session,
                payment_method=CASH_PM,
                system_expected_balance=opening + cash_sales,
                physical_closing_balance=opening + cash_sales,
                uncleared_amount=Decimal('0'),
            )
            print(f"  Session {d}: cash={cash_sales:,.0f}")


# ── 11. OFFICE USE ────────────────────────────────────────────────────────────

def make_office_use():
    """1–2 office use records per month (pens, paper etc for internal use)."""
    print("\n=== OFFICE USE ===")
    cat, _ = OfficeUseCategory.objects.get_or_create(name='Staff Use')
    # Low-value items suitable for office use
    office_specs = list(ProductSpec.objects.filter(
        cached_wac__gt=0, cached_wac__lte=500, current_stock__gt=5
    ))
    if not office_specs:
        print("  No suitable specs for office use")
        return

    months = [(2026, m) for m in range(1, 6)]
    for year, month in months:
        days = workdays(year, month)
        if year == 2026 and month == 5:
            days = [d for d in days if d <= date(2026, 5, 3)]
        if not days:
            continue

        n = random.randint(1, 2)
        for _ in range(n):
            spec = random.choice(office_specs)
            if spec.current_stock <= 0:
                continue
            d = random.choice(days)
            SaleOfficeUse.objects.create(
                product_spec=spec,
                office_use_category=cat,
                quantity=random.randint(1, 3),
                unit_price=spec.cached_wac,
                discount=Decimal('0'),
                sale_date=rand_time(d),
                reason='Internal office use',
            )
            print(f"  OfficeUse: {spec} on {d}")
            spec.refresh_from_db()


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("KIYABO DUKA — FAKE DATA GENERATOR (Jan–May 2026)")
    print("=" * 60)

    make_purchases()
    make_sales()
    make_return_inward()
    make_return_outward()
    make_drawings()
    make_debts()
    make_debt_returns()
    make_expense_payments()
    make_liability_payments()
    make_cash_sessions()
    make_office_use()

    print("\n" + "=" * 60)
    print("DONE. Summary:")
    expr = ExpressionWrapper(F('quantity')*F('unit_price')-F('discount'), output_field=DecimalField(max_digits=15,decimal_places=2))
    jan_start = make_aware(datetime(2026, 1, 1), EAT)
    print(f"  Sales (2026):        {Sale.objects.filter(sale_date__gte=jan_start).count()}")
    print(f"  Purchases (2026):    {Purchase.objects.filter(purchase_date__gte=jan_start).count()}")
    print(f"  Debts (2026):        {Debt.objects.filter(sale_date__gte=jan_start).count()}")
    print(f"  DebtReturns (2026):  {DebtReturn.objects.filter(return_date__gte=jan_start).count()}")
    print(f"  Drawings (2026):     {Drawing.objects.filter(sale_date__gte=jan_start).count()}")
    print(f"  Payments (2026):     {Payment.objects.filter(payment_date__gte=jan_start).count()}")
    print(f"  CashSessions (2026): {CashRegisterSession.objects.filter(session_date__gte=date(2026,1,1)).count()}")
    print(f"  ReturnInward (2026): {ReturnInward.objects.filter(sale_date__gte=jan_start).count()}")
    print(f"  ReturnOutward (2026):{ReturnOutward.objects.filter(sale_date__gte=jan_start).count()}")
    liability = LiabilityItem.objects.get(pk=1)
    print(f"  NMB Loan balance:    TZS {liability.current_balance:,.0f}")
    print("=" * 60)


if __name__ == '__main__':
    main()