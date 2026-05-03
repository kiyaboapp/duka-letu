from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from reports.views.base import BaseReportView
from inventory.models import Purchase, PurchaseDetail

_DEC = DecimalField(max_digits=15, decimal_places=2)


class PurchaseSummaryView(BaseReportView):
    template_name = 'reports/purchase_summary.html'

    def get_context(self, request, period):
        purchases = Purchase.objects.filter(
            purchase_date__date__range=(period.start, period.end)
        ).prefetch_related('details__product_spec__product').order_by('-purchase_date')

        line_expr = ExpressionWrapper(F('quantity') * F('unit_cost'), output_field=_DEC)
        total = PurchaseDetail.objects.filter(
            purchase__purchase_date__date__range=(period.start, period.end)
        ).aggregate(t=Coalesce(Sum(line_expr), Decimal('0'), output_field=_DEC))['t']

        return {'purchases': purchases, 'total': total}
