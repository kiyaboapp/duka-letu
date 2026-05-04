from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from reports.views.base import BaseReportView
from reports.services.accounting import AccountingService
from sales.models import Sale

_DEC = DecimalField(max_digits=15, decimal_places=2)
_rev_expr = ExpressionWrapper(F('quantity') * F('unit_price') - F('discount'), output_field=_DEC)


class ProductProfitabilityView(BaseReportView):
    template_name = 'reports/product_profitability.html'

    def get_context(self, request, period):
        # 1. Group sales by spec to get revenue and volume
        rows = (
            Sale.objects.filter(sale_date__date__range=(period.start, period.end))
            .values('product_spec__id', 'product_spec__product__name', 'product_spec__spec_value__value')
            .annotate(
                units_sold=Coalesce(Sum('quantity'), 0),
                revenue=Coalesce(Sum(_rev_expr), Decimal('0'), output_field=_DEC),
            )
            .order_by('-revenue')
        )
        
        data = []
        for r in rows:
            spec_id = r['product_spec__id']
            # 2. Get WAC for this specific spec using AccountingService
            svc = AccountingService(period.start, period.end, product_spec_id=spec_id)
            wac = svc.weighted_average_cost()
            
            # 3. Calculate COGS based on units sold in this period
            cogs = Decimal(r['units_sold']) * wac
            gp = r['revenue'] - cogs
            
            margin = (gp / r['revenue'] * 100).quantize(Decimal('0.1')) if r['revenue'] else Decimal('0')
            
            data.append({
                'product_spec__id': spec_id,
                'product_spec__product__name': r['product_spec__product__name'],
                'product_spec__spec_value__value': r['product_spec__spec_value__value'],
                'units_sold': r['units_sold'],
                'revenue': r['revenue'],
                'cogs': cogs,
                'gross_profit': gp,
                'margin_pct': margin
            })
            
        return {'rows': data}
