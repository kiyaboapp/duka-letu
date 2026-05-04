from decimal import Decimal
from datetime import date
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce

_DEC = DecimalField(max_digits=15, decimal_places=2)

# Reusable expression for (quantity * unit_price) - discount
def _sale_amount_expr():
    return ExpressionWrapper(
        F('quantity') * F('unit_price') - F('discount'),
        output_field=_DEC
    )

def _purchase_amount_expr():
    return ExpressionWrapper(
        F('quantity') * F('unit_cost'),
        output_field=_DEC
    )

def _simple_amount_expr():
    """For models with quantity * unit_price only (no discount)."""
    return ExpressionWrapper(
        F('quantity') * F('unit_price'),
        output_field=_DEC
    )


class AccountingService:
    """
    Weighted Average Cost inventory accounting engine.
    Mirrors modAccountings VBA logic 1:1.
    All monetary values in TZS (stored as Decimal).

    NOTE: 'amount' is a @property on all transaction models — not a DB column.
    All aggregations use ExpressionWrapper to compute values at the DB level.
    """

    def __init__(self, start_date: date, end_date: date, product_spec_id: int = None):
        self.start = start_date
        self.end = end_date
        self.spec_id = product_spec_id  # None = aggregate all products

    # ── HELPERS ─────────────────────────────────────────────────────────────

    def _qty(self, qs):
        return qs.aggregate(total=Coalesce(Sum('quantity'), Decimal('0'), output_field=_DEC))['total']

    def _sum_expr(self, qs, expr):
        return qs.aggregate(total=Coalesce(Sum(expr), Decimal('0')))['total']

    # ── QUANTITY FUNCTIONS ──────────────────────────────────────────────────

    def purchased_qty(self):
        from inventory.models import PurchaseDetail
        qs = PurchaseDetail.objects.filter(
            purchase__purchase_date__date__range=(self.start, self.end)
        )
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def sold_qty(self):
        from sales.models import Sale
        qs = Sale.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def credit_sales_qty(self):
        from credit.models import Debt
        qs = Debt.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def return_inwards_qty(self):
        from sales.models import ReturnInward
        qs = ReturnInward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(sale__product_spec_id=self.spec_id)
        return self._qty(qs)

    def return_outwards_qty(self):
        from inventory.models import ReturnOutward
        qs = ReturnOutward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(purchase_detail__product_spec_id=self.spec_id)
        return self._qty(qs)

    def office_use_qty(self):
        from sales.models import SaleOfficeUse
        qs = SaleOfficeUse.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    def drawings_qty(self):
        from sales.models import Drawing
        qs = Drawing.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._qty(qs)

    # ── MONETARY FUNCTIONS ──────────────────────────────────────────────────

    def direct_sales(self) -> Decimal:
        """Sum of (quantity * unit_price - discount) for all direct sales."""
        from sales.models import Sale
        qs = Sale.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._sum_expr(qs, _sale_amount_expr())

    def credit_sales(self) -> Decimal:
        """Sum of (quantity * unit_price - discount) for all credit sales."""
        from credit.models import Debt
        qs = Debt.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._sum_expr(qs, _sale_amount_expr())

    def return_inwards(self) -> Decimal:
        """Sum of (quantity * unit_price) for return inwards."""
        from sales.models import ReturnInward
        qs = ReturnInward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(sale__product_spec_id=self.spec_id)
        return self._sum_expr(qs, _simple_amount_expr())

    def net_sales(self) -> Decimal:
        return self.direct_sales() + self.credit_sales() - self.return_inwards()

    def purchases(self) -> Decimal:
        """Sum of (quantity * unit_cost) for all purchase details."""
        from inventory.models import PurchaseDetail
        qs = PurchaseDetail.objects.filter(
            purchase__purchase_date__date__range=(self.start, self.end)
        )
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        return self._sum_expr(qs, _purchase_amount_expr())

    def return_outwards(self) -> Decimal:
        """Sum of (quantity * unit_price) for return outwards."""
        from inventory.models import ReturnOutward
        qs = ReturnOutward.objects.filter(sale_date__date__range=(self.start, self.end))
        if self.spec_id:
            qs = qs.filter(purchase_detail__product_spec_id=self.spec_id)
        return self._sum_expr(qs, _simple_amount_expr())

    def net_purchases(self) -> Decimal:
        return self.purchases() - self.return_outwards()

    def weighted_average_cost(self) -> Decimal:
        """
        Weighted average cost per unit.
        Formula: total_purchase_cost / total_purchased_qty (all-time, not period-scoped).
        """
        from inventory.models import PurchaseDetail
        qs = PurchaseDetail.objects.all()
        if self.spec_id:
            qs = qs.filter(product_spec_id=self.spec_id)
        total_cost = self._sum_expr(qs, _purchase_amount_expr())
        total_qty = self._qty(qs)
        if total_qty == 0:
            return Decimal('0')
        return total_cost / total_qty

    def opening_stock_value(self) -> Decimal:
        """Opening stock = units in stock at start of period × WAC as of period start."""
        if self.spec_id:
            from datetime import timedelta
            prior_end = self.start - timedelta(days=1)
            prior_svc = AccountingService(date(2000, 1, 1), prior_end, self.spec_id)
            opening_qty = prior_svc._closing_stock_qty()
            wac = prior_svc.weighted_average_cost()
            return opening_qty * wac
        else:
            from inventory.models import ProductSpec
            total = Decimal('0')
            # Aggregate per-spec to avoid "Aggregate WAC" bug
            for spec_id in ProductSpec.objects.values_list('id', flat=True):
                total += AccountingService(self.start, self.end, spec_id).opening_stock_value()
            return total

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

    def closing_stock_qty(self) -> Decimal:
        """Closing stock = opening qty + period inflows - period outflows."""
        if self.spec_id:
            from datetime import timedelta
            prior_end = self.start - timedelta(days=1)
            prior_svc = AccountingService(date(2000, 1, 1), prior_end, self.spec_id)
            opening_qty = prior_svc._closing_stock_qty()
            period_delta = self._closing_stock_qty()
            return max(Decimal('0'), opening_qty + period_delta)
        else:
            from inventory.models import ProductSpec
            total = Decimal('0')
            for spec_id in ProductSpec.objects.values_list('id', flat=True):
                total += AccountingService(self.start, self.end, spec_id).closing_stock_qty()
            return total

    def closing_stock_value(self) -> Decimal:
        if self.spec_id:
            return self.closing_stock_qty() * self.weighted_average_cost()
        # Single aggregated query — no per-spec loop
        from catalog.models import ProductSpec
        from django.db.models import Sum, F, ExpressionWrapper
        total = ProductSpec.objects.aggregate(
            val=Coalesce(
                Sum(ExpressionWrapper(F('current_stock') * F('cached_wac'), output_field=_DEC)),
                Decimal('0'),
                output_field=_DEC,
            )
        )['val']
        return total

    def cogs(self) -> Decimal:
        """COGS = Opening Stock + Net Purchases - Closing Stock"""
        return self.opening_stock_value() + self.net_purchases() - self.closing_stock_value()

    def gross_profit(self) -> Decimal:
        return self.net_sales() - self.cogs()

    def operating_expenses(self) -> dict:
        from finance.models import Payment, PaymentAllocation
        from django.db.models import Sum
        from collections import defaultdict

        # Direct payments
        payments = (
            Payment.objects
            .filter(
                payment_date__date__range=(self.start, self.end),
                payment_type='EXPENSE',
                expense_item__isnull=False,
            )
            .values('expense_item__expense_type__name')
            .annotate(total=Sum('amount_paid'))
            .order_by('expense_item__expense_type__name')
        )
        lines = {row['expense_item__expense_type__name']: row['total'] for row in payments}

        # Prepayment allocations (rent paid in advance shows here)
        allocations = (
            PaymentAllocation.objects
            .filter(
                allocation_date__date__range=(self.start, self.end),
                obligation__expense_item__isnull=False,
            )
            .values('obligation__expense_item__expense_type__name')
            .annotate(total=Sum('amount_allocated'))
        )
        for row in allocations:
            key = row['obligation__expense_item__expense_type__name']
            lines[key] = lines.get(key, Decimal('0')) + row['total']

        # Office use cost valued at WAC
        office_cost = Decimal('0')
        if self.spec_id:
            office_cost = self.office_use_qty() * self.weighted_average_cost()
        else:
            from catalog.models import ProductSpec
            for spec_id in ProductSpec.objects.values_list('id', flat=True):
                spec_svc = AccountingService(self.start, self.end, spec_id)
                office_cost += spec_svc.office_use_qty() * spec_svc.weighted_average_cost()

        if office_cost:
            lines['Office Use / Customer Care'] = lines.get('Office Use / Customer Care', Decimal('0')) + office_cost

        total = sum(lines.values(), Decimal('0'))
        return {'lines': lines, 'total': total}

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
        closing_qty = self.closing_stock_qty()
        cogs = cogas - closing
        gross_profit = net_sales - cogs

        expenses = self.operating_expenses()
        net_profit = gross_profit - expenses['total']

        return {
            'period_start': self.start,
            'period_end': self.end,
            'direct_sales': direct,
            'credit_sales': credit,
            'return_inwards': ret_in,
            'net_sales': net_sales,
            'opening_stock': opening,
            'purchases': purch,
            'carriage_inwards': Decimal('0'),
            'return_outwards': ret_out,
            'net_purchases': net_purch,
            'cogas': cogas,
            'closing_stock': closing,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'expense_lines': expenses['lines'],
            'total_expenses': expenses['total'],
            'net_profit': net_profit,
        }
