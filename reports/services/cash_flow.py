from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from reports.services.accounting import AccountingService
from reports.services.balance_sheet import BalanceSheetService

_DEC = DecimalField(max_digits=15, decimal_places=2)
_draw_expr = ExpressionWrapper(
    F('quantity') * F('unit_price') - F('discount'), output_field=_DEC
)


class CashFlowService:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.acct = AccountingService(start, end)

    def net_profit(self) -> Decimal:
        from reports.services.expenses import ExpenseService
        return self.acct.gross_profit() - ExpenseService(self.start, self.end).total()

    def depreciation_add_back(self) -> Decimal:
        from assets.models import Asset
        months = Decimal((self.end - self.start).days) / Decimal('30.44')
        return sum(
            a.monthly_depreciation_charge * months
            for a in Asset.objects.filter(acquisition_date__lte=self.end, disposal_date__isnull=True)
        )

    def working_capital_changes(self) -> dict:
        from datetime import timedelta
        bs_open = BalanceSheetService(self.start - timedelta(days=1))
        bs_close = BalanceSheetService(self.end)
        return {
            'stock_change': -(bs_close.inventory_value() - bs_open.inventory_value()),
            'receivables_change': -(bs_close.net_receivables() - bs_open.net_receivables()),
            'payables_change': bs_close.current_liabilities() - bs_open.current_liabilities(),
        }

    def financing_cash_flow(self) -> dict:
        from sales.models import Drawing
        from finance.models import LiabilityPaymentDetail
        # Drawings: cash drawings use cash_amount; goods drawings use WAC
        cash_draw = Drawing.objects.filter(
            sale_date__date__range=(self.start, self.end), drawing_type='CASH'
        ).aggregate(t=Coalesce(Sum('cash_amount'), Decimal('0'), output_field=_DEC))['t']
        goods_draw = Drawing.objects.filter(
            sale_date__date__range=(self.start, self.end), drawing_type='GOODS'
        ).aggregate(t=Coalesce(Sum(_draw_expr), Decimal('0'), output_field=_DEC))['t']
        drawings = cash_draw + goods_draw
        principal = LiabilityPaymentDetail.objects.filter(
            payment_date__date__range=(self.start, self.end)
        ).aggregate(t=Coalesce(Sum('principal_amount'), Decimal('0'), output_field=_DEC))['t']
        return {'drawings': -drawings, 'loan_repayment': -principal, 'total': -drawings - principal}

    def to_cash_flow(self) -> dict:
        wc = self.working_capital_changes()
        fin = self.financing_cash_flow()
        np = self.net_profit()
        dep = self.depreciation_add_back()
        operating = np + dep + wc['stock_change'] + wc['receivables_change'] + wc['payables_change']
        return {
            'period_start': self.start, 'period_end': self.end,
            'net_profit': np, 'depreciation': dep,
            'stock_change': wc['stock_change'],
            'receivables_change': wc['receivables_change'],
            'payables_change': wc['payables_change'],
            'operating_cash_flow': operating,
            'drawings': fin['drawings'],
            'loan_repayment': fin['loan_repayment'],
            'financing_cash_flow': fin['total'],
            'investing_cash_flow': Decimal('0'),
            'net_cash_movement': operating + fin['total'],
        }
