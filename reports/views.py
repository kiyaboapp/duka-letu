from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
WEASYPRINT_AVAILABLE = False
HTML = None

def _get_weasyprint():
    global WEASYPRINT_AVAILABLE, HTML
    if WEASYPRINT_AVAILABLE:
        return HTML
    try:
        from weasyprint import HTML as WPHTML
        HTML = WPHTML
        WEASYPRINT_AVAILABLE = True
        return WPHTML
    except Exception:
        return None
from .services.accounting import AccountingService
from catalog.models import ProductSpec
from credit.models import Debtor, Debt


class IncomeStatementView(View):
    def get(self, request):
        period = request.GET.get('period', 'month')
        today = timezone.now().date()

        if period == 'month':
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif period == 'quarter':
            month = (today.month - 1) // 3 * 3 + 1
            start = today.replace(month=month, day=1)
            if month + 2 > 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=month + 2, day=1) - timedelta(days=1)
        else:  # year
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)

        service = AccountingService(start, end)
        data = service.to_income_statement()

        format_type = request.GET.get('format', 'html')
        if format_type == 'pdf':
            return self._render_pdf(data, request)
        else:
            return render(request, 'reports/income_statement.html', {'data': data})

    def _render_pdf(self, data, request):
        WPHTML = _get_weasyprint()
        if not WPHTML:
            return HttpResponse("PDF generation requires WeasyPrint with GTK libraries. Please install GTK or use HTML format.", status=503)
        html_content = render(request, 'reports/income_statement_pdf.html', {'data': data}).content
        pdf = WPHTML(string=html_content).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="income_statement_{data["period_end"]}.pdf"'
        return response


class StockReportView(View):
    def get(self, request):
        products = ProductSpec.objects.select_related('product', 'spec_value').all()
        low_stock = [p for p in products if p.is_low_stock]
        out_of_stock = [p for p in products if p.is_out_of_stock]

        return render(request, 'reports/stock_report.html', {
            'products': products,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
        })


class DebtorAgingView(View):
    def get(self, request):
        debtors = Debtor.objects.prefetch_related('debts').all()
        aging_data = []

        for debtor in debtors:
            aging = self._calculate_aging(debtor)
            if aging['total'] > 0:
                aging_data.append({
                    'debtor': debtor,
                    **aging
                })

        return render(request, 'reports/debtor_aging.html', {
            'aging_data': aging_data,
        })

    def _calculate_aging(self, debtor):
        today = date.today()
        b0_30 = Decimal('0')
        b31_60 = Decimal('0')
        b61_90 = Decimal('0')
        b90_plus = Decimal('0')

        for debt in debtor.debts.all():
            balance = debt.balance
            if balance <= 0:
                continue
            days_overdue = (today - debt.expected_payment_date).days if debt.expected_payment_date else 0

            if days_overdue <= 30:
                b0_30 += balance
            elif days_overdue <= 60:
                b31_60 += balance
            elif days_overdue <= 90:
                b61_90 += balance
            else:
                b90_plus += balance

        return {
            'bucket_0_30': b0_30,
            'bucket_31_60': b31_60,
            'bucket_61_90': b61_90,
            'bucket_90_plus': b90_plus,
            'total': b0_30 + b31_60 + b61_90 + b90_plus,
        }


def index(request):
    return render(request, 'reports/index.html')

# Create your views here.
