from django.http import HttpResponse
from django.shortcuts import render
from reports.views.base import BaseReportView
from reports.services.accounting import AccountingService
from reports.services.expenses import ExpenseService

WEASYPRINT_AVAILABLE = False
_HTML = None


def _get_weasyprint():
    global WEASYPRINT_AVAILABLE, _HTML
    if WEASYPRINT_AVAILABLE:
        return _HTML
    try:
        from weasyprint import HTML as WP
        _HTML = WP
        WEASYPRINT_AVAILABLE = True
        return WP
    except Exception:
        return None


class IncomeStatementView(BaseReportView):
    template_name = 'reports/income_statement.html'
    default_preset = 'this_month'

    def get_context(self, request, period):
        acct = AccountingService(period.start, period.end)
        exp = ExpenseService(period.start, period.end)
        data = acct.to_income_statement()
        data['total_expenses'] = exp.total()
        data['expenses_by_type'] = exp.by_type()
        data['net_profit'] = data.get('gross_profit', 0) - data['total_expenses']
        return {'data': data}

    def get(self, request):
        from reports.forms import ReportPeriodForm
        from reports.periods import ReportPeriod
        form = ReportPeriodForm(request.GET or None)
        period = form.resolved_period(self.default_preset) if form.is_valid() else ReportPeriod.resolve(default_preset=self.default_preset)
        ctx = self.get_context(request, period)
        ctx['form'] = form
        ctx['period'] = period
        if request.GET.get('format') == 'pdf':
            WP = _get_weasyprint()
            if not WP:
                return HttpResponse('PDF requires WeasyPrint.', status=503)
            html = render(request, 'reports/income_statement_pdf.html', ctx).content
            pdf = WP(string=html).write_pdf()
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="income_statement_{period.end}.pdf"'
            return resp
        return render(request, self.template_name, ctx)
