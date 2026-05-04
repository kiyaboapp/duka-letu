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
            a.get_accumulated_depreciation(self.as_of)
            for a in Asset.objects.filter(acquisition_date__lte=self.as_of, disposal_date__isnull=True)
        )

    def net_book_value_assets(self) -> Decimal:
        return self.fixed_assets_cost() - self.accumulated_depreciation_total()

    # ── Current assets ───────────────────────────────────────────────────────

    def inventory_value(self) -> Decimal:
        from reports.services.accounting import AccountingService
        from datetime import date
        # Point-in-time valuation using the fixed per-spec logic
        svc = AccountingService(date(2000, 1, 1), self.as_of)
        return svc.closing_stock_value()

    def _get_debt_balance_as_of(self, debt) -> Decimal:
        """Calculates debt balance specifically as of self.as_of."""
        from credit.models import DebtReturn
        from django.db.models import Sum
        debt_total = (debt.quantity * debt.unit_price) - debt.discount
        repaid_as_of = DebtReturn.objects.filter(
            debt=debt,
            return_date__date__lte=self.as_of
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        return max(debt_total - repaid_as_of, Decimal('0'))

    def gross_receivables(self) -> Decimal:
        from credit.models import Debt
        total = Decimal('0')
        for debt in Debt.objects.filter(sale_date__date__lte=self.as_of):
            total += self._get_debt_balance_as_of(debt)
        return total

    def bad_debt_provision(self) -> Decimal:
        from credit.models import Debt
        provision = Decimal('0')
        for debt in Debt.objects.filter(sale_date__date__lte=self.as_of):
            balance = self._get_debt_balance_as_of(debt)
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

    def _get_liability_balance_as_of(self, item) -> Decimal:
        """Calculates liability balance specifically as of self.as_of."""
        from finance.models import LiabilityPaymentDetail
        from django.db.models import Sum
        paid_as_of = LiabilityPaymentDetail.objects.filter(
            liability_item=item,
            payment_date__date__lte=self.as_of
        ).aggregate(t=Sum('principal_amount'))['t'] or Decimal('0')
        return max(item.original_amount - paid_as_of, Decimal('0'))

    def long_term_liabilities(self) -> Decimal:
        from finance.models import LiabilityItem
        total = Decimal('0')
        for item in LiabilityItem.objects.filter(start_date__lte=self.as_of):
            # Only include if it was active and not fully matured/paid by this date
            # Actually, we should include all that had a balance on this date.
            balance = self._get_liability_balance_as_of(item)
            if balance > 0:
                # If maturity_date exists and is in the future, it's long-term
                if not item.maturity_date or item.maturity_date > self.as_of:
                    total += balance
        return total

    def _get_obligation_balance_as_of(self, obligation) -> Decimal:
        """Calculates obligation balance specifically as of self.as_of."""
        from finance.models import Payment
        from django.db.models import Sum
        paid_as_of = Payment.objects.filter(
            obligation=obligation,
            payment_date__date__lte=self.as_of
        ).aggregate(t=Sum('amount_paid'))['t'] or Decimal('0')
        return max(obligation.amount_due - obligation.prepayment_applied - paid_as_of, Decimal('0'))

    def current_liabilities(self) -> Decimal:
        from finance.models import PaymentObligation
        result = Decimal('0')
        for o in PaymentObligation.objects.filter(due_date__lte=self.as_of):
            result += self._get_obligation_balance_as_of(o)
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
