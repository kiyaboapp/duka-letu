from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce

_DEC = DecimalField(max_digits=15, decimal_places=2)


class BalanceSheetService:
    def __init__(self, as_of_date):
        self.as_of = as_of_date

    # ── Non-current assets ───────────────────────────────────────────────────

    def fixed_assets_cost(self) -> Decimal:
        from assets.models import Asset
        return Asset.objects.filter(
            acquisition_date__lte=self.as_of, disposal_date__isnull=True
        ).aggregate(t=Coalesce(Sum('cost_price'), Decimal('0'), output_field=_DEC))['t']

    def accumulated_depreciation_total(self) -> Decimal:
        from assets.models import Asset
        return sum(
            a.accumulated_depreciation
            for a in Asset.objects.filter(acquisition_date__lte=self.as_of, disposal_date__isnull=True)
        )

    def net_book_value_assets(self) -> Decimal:
        return self.fixed_assets_cost() - self.accumulated_depreciation_total()

    # ── Current assets ───────────────────────────────────────────────────────

    def inventory_value(self) -> Decimal:
        from catalog.models import ProductSpec
        return ProductSpec.objects.aggregate(
            t=Coalesce(Sum('cached_stock_value'), Decimal('0'), output_field=_DEC)
        )['t']

    def gross_receivables(self) -> Decimal:
        from credit.models import Debt, DebtReturn
        debt_expr = ExpressionWrapper(
            F('quantity') * F('unit_price') - F('discount'), output_field=_DEC
        )
        total_debts = Debt.objects.filter(
            sale_date__date__lte=self.as_of
        ).aggregate(t=Coalesce(Sum(debt_expr), Decimal('0'), output_field=_DEC))['t']
        total_repaid = DebtReturn.objects.filter(
            return_date__date__lte=self.as_of
        ).aggregate(t=Coalesce(Sum('amount'), Decimal('0'), output_field=_DEC))['t']
        return max(total_debts - total_repaid, Decimal('0'))

    def bad_debt_provision(self) -> Decimal:
        from credit.models import Debt
        provision = Decimal('0')
        for debt in Debt.objects.filter(sale_date__date__lte=self.as_of).select_related():
            balance = debt.balance
            if balance <= 0 or not debt.expected_payment_date:
                continue
            days = (self.as_of - debt.expected_payment_date).days
            if days > 90:
                provision += balance * Decimal('0.10')
            elif days > 60:
                provision += balance * Decimal('0.05')
            elif days > 30:
                provision += balance * Decimal('0.01')
        return provision.quantize(Decimal('0.01'))

    def net_receivables(self) -> Decimal:
        return self.gross_receivables() - self.bad_debt_provision()

    def cash_and_equivalents(self) -> Decimal:
        """From latest closed CashRegisterSession, or 0 if none."""
        from finance.models import CashRegisterSession
        session = CashRegisterSession.objects.filter(
            session_date__lte=self.as_of, status__in=['CLOSED', 'VARIANCE']
        ).order_by('-session_date').first()
        if not session:
            return Decimal('0')
        return (
            session.closing_balance_for('CASH') +
            session.closing_balance_for('MOBILE_MONEY') +
            session.closing_balance_for('BANK')
        )

    def total_current_assets(self) -> Decimal:
        return self.inventory_value() + self.net_receivables() + self.cash_and_equivalents()

    def total_assets(self) -> Decimal:
        return self.net_book_value_assets() + self.total_current_assets()

    # ── Liabilities ──────────────────────────────────────────────────────────

    def long_term_liabilities(self) -> Decimal:
        from finance.models import LiabilityItem
        return sum(
            item.current_balance
            for item in LiabilityItem.objects.filter(is_active=True)
            if item.maturity_date and item.maturity_date > self.as_of
        )

    def current_liabilities(self) -> Decimal:
        from finance.models import PaymentObligation
        # balance = amount_due - prepayment_applied - amount_paid (all real DB columns)
        result = Decimal('0')
        for o in PaymentObligation.objects.filter(due_date__lte=self.as_of):
            b = o.amount_due - o.prepayment_applied - o.amount_paid
            if b > 0:
                result += b
        return result

    def total_liabilities(self) -> Decimal:
        return self.long_term_liabilities() + self.current_liabilities()

    def total_equity(self) -> Decimal:
        return self.total_assets() - self.total_liabilities()

    def to_balance_sheet(self) -> dict:
        ta = self.total_assets()
        tl = self.total_liabilities()
        eq = self.total_equity()
        return {
            'as_of': self.as_of,
            'fixed_assets_cost': self.fixed_assets_cost(),
            'accumulated_depreciation': self.accumulated_depreciation_total(),
            'net_book_value': self.net_book_value_assets(),
            'inventory': self.inventory_value(),
            'gross_receivables': self.gross_receivables(),
            'bad_debt_provision': self.bad_debt_provision(),
            'net_receivables': self.net_receivables(),
            'cash_and_equivalents': self.cash_and_equivalents(),
            'total_current_assets': self.total_current_assets(),
            'total_assets': ta,
            'long_term_liabilities': self.long_term_liabilities(),
            'current_liabilities': self.current_liabilities(),
            'total_liabilities': tl,
            'total_equity': eq,
            'equation_holds': abs(ta - tl - eq) < Decimal('1'),
        }
