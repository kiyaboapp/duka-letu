from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from reports.views.base import BaseReportView
from catalog.models import ProductSpec
from sales.models import Sale

_DEC = DecimalField(max_digits=15, decimal_places=2)
_rev_expr = ExpressionWrapper(F('quantity') * F('unit_price') - F('discount'), output_field=_DEC)
_cost_expr = ExpressionWrapper(F('quantity') * F('unit_cost'), output_field=_DEC)


class ProductProfitabilityView(BaseReportView):
    template_name = 'reports/product_profitability.html'

    def get_context(self, request, period):
        rows = (
            Sale.objects.filter(sale_date__date__range=(period.start, period.end))
            .values('product_spec__id', 'product_spec__product__name', 'product_spec__spec_value__value')
            .annotate(
                units_sold=Coalesce(Sum('quantity'), 0),
                revenue=Coalesce(Sum(_rev_expr), Decimal('0'), output_field=_DEC),
                cogs=Coalesce(Sum(_cost_expr), Decimal('0'), output_field=_DEC),
            )
            .order_by('-revenue')
        )
        data = []
        for r in rows:
            gp = r['revenue'] - r['cogs']
            margin = (gp / r['revenue'] * 100).quantize(Decimal('0.1')) if r['revenue'] else Decimal('0')
            data.append({**r, 'gross_profit': gp, 'margin_pct': margin})
        return {'rows': data}
