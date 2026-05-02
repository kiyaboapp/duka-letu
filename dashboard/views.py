from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from datetime import date, timedelta
from decimal import Decimal
from sales.models import Sale
from credit.models import Debt, DebtReturn
from catalog.models import ProductSpec
from finance.models import PaymentObligation

_DEC = DecimalField(max_digits=15, decimal_places=2)
_revenue_expr = ExpressionWrapper(
    F('quantity') * F('unit_price') - F('discount'),
    output_field=_DEC
)


def _revenue(qs):
    return qs.aggregate(
        total=Coalesce(Sum(_revenue_expr, output_field=_DEC), Decimal('0'))
    )['total']


def dashboard_view(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    yesterday = today - timedelta(days=1)

    # ── Revenue ──────────────────────────────────────────────────────────────
    today_revenue = _revenue(Sale.objects.filter(sale_date__date=today))
    yesterday_revenue = _revenue(Sale.objects.filter(sale_date__date=yesterday))
    mtd_revenue = _revenue(Sale.objects.filter(sale_date__date__gte=month_start))
    ytd_revenue = _revenue(Sale.objects.filter(sale_date__date__gte=year_start))
    today_transactions = Sale.objects.filter(sale_date__date=today).count()

    # Revenue delta vs yesterday
    if yesterday_revenue > 0:
        revenue_delta_pct = int(((today_revenue - yesterday_revenue) / yesterday_revenue) * 100)
    else:
        revenue_delta_pct = None

    # ── Receivables ───────────────────────────────────────────────────────────
    # Compute at DB level: sum of (qty*price-discount) minus sum of returns
    debt_expr = ExpressionWrapper(
        F('quantity') * F('unit_price') - F('discount'),
        output_field=_DEC
    )
    total_debt_issued = Debt.objects.aggregate(
        t=Coalesce(Sum(debt_expr, output_field=_DEC), Decimal('0'))
    )['t']
    total_debt_returned = DebtReturn.objects.aggregate(
        t=Coalesce(Sum('amount', output_field=_DEC), Decimal('0'))
    )['t']
    outstanding_receivables = total_debt_issued - total_debt_returned

    # Overdue debts
    overdue_debts = Debt.objects.filter(
        expected_payment_date__lt=today,
        expected_payment_date__isnull=False
    ).count()

    # ── Stock alerts ──────────────────────────────────────────────────────────
    low_stock = ProductSpec.objects.filter(
        current_stock__gt=0,
        current_stock__lte=F('reorder_level')
    ).count()
    out_of_stock = ProductSpec.objects.filter(current_stock__lte=0).count()
    total_products = ProductSpec.objects.count()

    # ── Obligations ───────────────────────────────────────────────────────────
    overdue_obligations = PaymentObligation.objects.filter(
        due_date__lt=today,
    ).exclude(
        amount_paid__gte=F('amount_due') - F('prepayment_applied')
    ).count()

    # ── Recent sales ──────────────────────────────────────────────────────────
    recent_sales = Sale.objects.select_related(
        'product_spec__product', 'product_spec__spec_value', 'payment_method'
    ).order_by('-sale_date')[:12]

    # ── Top products today ────────────────────────────────────────────────────
    top_products = (
        Sale.objects.filter(sale_date__date=today)
        .values('product_spec__product__name', 'product_spec__spec_value__value', 'product_spec_id')
        .annotate(
            total_qty=Coalesce(Sum('quantity'), 0, output_field=IntegerField()),
            total_rev=Coalesce(Sum(_revenue_expr, output_field=_DEC), Decimal('0'))
        )
        .order_by('-total_rev')[:5]
    )

    # ── Low stock products ────────────────────────────────────────────────────
    low_stock_products = ProductSpec.objects.filter(
        current_stock__lte=F('reorder_level')
    ).select_related('product', 'spec_value').order_by('current_stock')[:8]

    context = {
        'today': today,
        'today_revenue': today_revenue,
        'yesterday_revenue': yesterday_revenue,
        'revenue_delta_pct': revenue_delta_pct,
        'today_transactions': today_transactions,
        'mtd_revenue': mtd_revenue,
        'ytd_revenue': ytd_revenue,
        'outstanding_receivables': outstanding_receivables,
        'overdue_debts': overdue_debts,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_products': total_products,
        'overdue_obligations': overdue_obligations,
        'recent_sales': recent_sales,
        'top_products': top_products,
        'low_stock_products': low_stock_products,
    }

    return render(request, 'dashboard/index.html', context)
