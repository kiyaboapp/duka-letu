from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from reports.views.base import BaseReportView
from sales.models import Drawing

_DEC = DecimalField(max_digits=15, decimal_places=2)


class DrawingsSummaryView(BaseReportView):
    template_name = 'reports/drawings_summary.html'

    def get_context(self, request, period):
        drawings = Drawing.objects.filter(
            sale_date__date__range=(period.start, period.end)
        ).select_related('product_spec__product', 'product_spec__spec_value').order_by('-sale_date')

        cash_total = drawings.filter(drawing_type='CASH').aggregate(
            t=Coalesce(Sum('cash_amount'), Decimal('0'), output_field=_DEC)
        )['t']
        goods_expr = ExpressionWrapper(F('quantity') * F('unit_price') - F('discount'), output_field=_DEC)
        goods_total = drawings.filter(drawing_type='GOODS').aggregate(
            t=Coalesce(Sum(goods_expr), Decimal('0'), output_field=_DEC)
        )['t']

        return {
            'drawings': drawings,
            'cash_total': cash_total,
            'goods_total': goods_total,
            'grand_total': cash_total + goods_total,
        }
