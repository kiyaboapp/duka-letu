from django.views import View
from django.shortcuts import render
from reports.forms import ReportPeriodForm
from reports.periods import ReportPeriod


class BaseReportView(View):
    template_name = None
    default_preset = 'this_month'

    def get_context(self, request, period):
        return {}

    def get(self, request):
        form = ReportPeriodForm(request.GET or None)
        period = form.resolved_period(self.default_preset) if form.is_valid() else ReportPeriod.resolve(default_preset=self.default_preset)
        ctx = self.get_context(request, period)
        ctx['form'] = form
        ctx['period'] = period
        return render(request, self.template_name, ctx)
