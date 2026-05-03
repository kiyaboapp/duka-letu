from decimal import Decimal
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce

_DEC = DecimalField(max_digits=15, decimal_places=2)
_sale_expr = ExpressionWrapper(F('quantity') * F('unit_price') - F('discount'), output_field=_DEC)
_debt_expr = ExpressionWrapper(F('quantity') * F('unit_price') - F('discount'), output_field=_DEC)
_ret_expr = ExpressionWrapper(F('quantity') * F('unit_price'), output_field=_DEC)


class DailySalesSummaryService:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def _sales_qs(self):
        from sales.models import Sale
        return Sale.objects.filter(sale_date__date__range=(self.start, self.end))

    def _debt_qs(self):
        from credit.models import Debt
        return Debt.objects.filter(sale_date__date__range=(self.start, self.end))

    def by_payment_method(self):
        return list(
            self._sales_qs()
            .values(
                'payment_method__name',
                'payment_method__category_link__category__code',
                'payment_method__category_link__category__name',
            )
            .annotate(
                count=Count('id'),
                total=Coalesce(Sum(_sale_expr), Decimal('0'), output_field=_DEC),
            )
            .order_by('payment_method__name')
        )

    def by_transaction_type(self) -> dict:
        from sales.models import ReturnInward
        direct = self._sales_qs().aggregate(
            t=Coalesce(Sum(_sale_expr), Decimal('0'), output_field=_DEC)
        )['t']
        credit = self._debt_qs().aggregate(
            t=Coalesce(Sum(_debt_expr), Decimal('0'), output_field=_DEC)
        )['t']
        returns = ReturnInward.objects.filter(
            sale_date__date__range=(self.start, self.end)
        ).aggregate(t=Coalesce(Sum(_ret_expr), Decimal('0'), output_field=_DEC))['t']
        return {
            'direct_sales': direct, 'credit_sales': credit,
            'return_inwards': returns,
            'gross_sales': direct + credit,
            'net_sales': direct + credit - returns,
        }

    def top_products(self, limit=10):
        return list(
            self._sales_qs()
            .values('product_spec__product__name', 'product_spec__spec_value__value')
            .annotate(
                units=Coalesce(Sum('quantity'), 0),
                revenue=Coalesce(Sum(_sale_expr), Decimal('0'), output_field=_DEC),
            )
            .order_by('-revenue')[:limit]
        )

    def credit_sales_detail(self):
        return self._debt_qs().select_related('debtor', 'product_spec__product').order_by('-sale_date')

    def totals(self) -> dict:
        return self.by_transaction_type()
