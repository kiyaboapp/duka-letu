from reports.views.base import BaseReportView
from reports.services.cash_flow import CashFlowService


class CashFlowView(BaseReportView):
    template_name = 'reports/cash_flow.html'

    def get_context(self, request, period):
        svc = CashFlowService(period.start, period.end)
        return {'data': svc.to_cash_flow()}
