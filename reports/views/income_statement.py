from django.http import HttpResponse
from django.shortcuts import render
from reports.views.base import BaseReportView
from reports.services.accounting import AccountingService
from reports.services.expenses import ExpenseService
from decimal import Decimal


class IncomeStatementView(BaseReportView):
    template_name = 'reports/income_statement.html'
    default_preset = 'this_month'

    def get_context(self, request, period):
        acct = AccountingService(period.start, period.end)
        exp = ExpenseService(period.start, period.end)
        data = acct.to_income_statement()
        data['total_expenses'] = exp.total()
        data['expenses_by_type'] = exp.by_type()
        data['net_profit'] = data.get('gross_profit', Decimal('0')) - data['total_expenses']
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
            return self._render_pdf(ctx, period)
        return render(request, self.template_name, ctx)

    def _render_pdf(self, ctx, period):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        import io

        data = ctx['data']
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
        styles = getSampleStyleSheet()
        bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold')
        normal = styles['Normal']

        def tzs(v):
            return f"TZS {v:,.0f}" if v >= 0 else f"(TZS {abs(v):,.0f})"

        rows = [
            [Paragraph('Income Statement', bold), ''],
            [f"{period.start} to {period.end}", ''],
            ['', ''],
            [Paragraph('REVENUE', bold), ''],
            ['Direct Sales', tzs(data['direct_sales'])],
            ['Credit Sales', tzs(data['credit_sales'])],
            ['Less: Returns Inward', f"({tzs(data['return_inwards'])})"],
            [Paragraph('Net Sales', bold), Paragraph(tzs(data['net_sales']), bold)],
            ['', ''],
            [Paragraph('COST OF GOODS SOLD', bold), ''],
            ['Opening Stock', tzs(data['opening_stock'])],
            ['Add: Purchases', tzs(data['purchases'])],
            ['Less: Returns Outward', f"({tzs(data['return_outwards'])})"],
            ['Net Purchases', tzs(data['net_purchases'])],
            ['COGAS', tzs(data['cogas'])],
            ['Less: Closing Stock', f"({tzs(data['closing_stock'])})"],
            [Paragraph('COGS', bold), Paragraph(tzs(data['cogs']), bold)],
            [Paragraph('Gross Profit', bold), Paragraph(tzs(data['gross_profit']), bold)],
            ['', ''],
            [Paragraph('OPERATING EXPENSES', bold), ''],
        ]
        for name, amount in data.get('expense_lines', {}).items():
            rows.append([name, tzs(amount)])
        rows += [
            [Paragraph('Total Expenses', bold), Paragraph(tzs(data['total_expenses']), bold)],
            ['', ''],
            [Paragraph('NET PROFIT', bold), Paragraph(tzs(data['net_profit']), bold)],
        ]

        t = Table(rows, colWidths=[12*cm, 5*cm])
        t.setStyle(TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('LINEBELOW', (0,7), (-1,7), 0.5, colors.grey),
            ('LINEBELOW', (0,17), (-1,17), 0.5, colors.grey),
            ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))

        doc.build([t])
        buf.seek(0)
        resp = HttpResponse(buf, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="income_statement_{period.end}.pdf"'
        return resp
