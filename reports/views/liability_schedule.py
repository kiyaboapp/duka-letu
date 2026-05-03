from django.shortcuts import render
from finance.models import LiabilityItem


def liability_schedule(request):
    liabilities = LiabilityItem.objects.filter(is_active=True).prefetch_related(
        'payment_details__payment'
    ).select_related('liability_type__category')
    return render(request, 'reports/liability_schedule.html', {'liabilities': liabilities})
