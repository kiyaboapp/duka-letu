from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import PaymentObligation, Payment


def index(request):
    today = timezone.now().date()

    obligations = PaymentObligation.objects.select_related(
        'expense_item__expense_type', 'liability_item'
    ).order_by('due_date')

    total_obligations = obligations.count()

    overdue_obligations = obligations.filter(due_date__lt=today).exclude(
        amount_paid__gte=F('amount_due') - F('prepayment_applied')
    ).count()

    # Paid this month
    month_start = today.replace(day=1)
    paid_this_month = Payment.objects.filter(
        payment_date__date__gte=month_start,
        payment_type='EXPENSE',
    ).aggregate(total=Coalesce(Sum('amount_paid'), Decimal('0')))['total']

    return render(request, 'finance/index.html', {
        'obligations': obligations,
        'total_obligations': total_obligations,
        'overdue_obligations': overdue_obligations,
        'paid_this_month': paid_this_month,
    })
