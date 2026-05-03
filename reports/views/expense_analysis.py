from reports.views.base import BaseReportView
from reports.services.expenses import ExpenseService


class ExpenseAnalysisView(BaseReportView):
    template_name = 'reports/expense_analysis.html'

    def get_context(self, request, period):
        svc = ExpenseService(period.start, period.end)
        return {
            'by_type': svc.by_type(),
            'by_item': svc.by_item(),
            'total': svc.total(),
            'obligations_summary': svc.obligations_summary(),
        }
