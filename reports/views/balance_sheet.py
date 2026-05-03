from django.utils import timezone
from reports.views.base import BaseReportView
from reports.services.balance_sheet import BalanceSheetService


class BalanceSheetView(BaseReportView):
    template_name = 'reports/balance_sheet.html'
    default_preset = 'this_month'

    def get_context(self, request, period):
        svc = BalanceSheetService(period.end)
        return {'data': svc.to_balance_sheet()}
