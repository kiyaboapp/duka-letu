from reports.views.base import BaseReportView
from finance.models import CashRegisterSession


class CashReconciliationView(BaseReportView):
    template_name = 'reports/cash_reconciliation.html'

    def get_context(self, request, period):
        sessions = CashRegisterSession.objects.filter(
            session_date__range=(period.start, period.end)
        ).prefetch_related('balances__payment_method').order_by('-session_date')
        return {'sessions': sessions}
