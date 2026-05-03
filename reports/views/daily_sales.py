from reports.views.base import BaseReportView
from reports.services.sales_summary import DailySalesSummaryService


class DailySalesView(BaseReportView):
    template_name = 'reports/daily_sales.html'
    default_preset = 'today'

    def get_context(self, request, period):
        svc = DailySalesSummaryService(period.start, period.end)
        return {
            'totals': svc.totals(),
            'by_payment_method': svc.by_payment_method(),
            'top_products': svc.top_products(10),
            'credit_sales': svc.credit_sales_detail(),
        }
