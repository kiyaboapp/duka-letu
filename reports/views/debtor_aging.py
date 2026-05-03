from datetime import date
from decimal import Decimal
from django.shortcuts import render
from credit.models import Debtor


def debtor_aging(request):
    debtors = Debtor.objects.prefetch_related('debts').all()
    aging_data = []
    today = date.today()

    for debtor in debtors:
        b0, b31, b61, b91 = Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0')
        for debt in debtor.debts.all():
            bal = debt.balance
            if bal <= 0:
                continue
            days = (today - debt.expected_payment_date).days if debt.expected_payment_date else 0
            if days <= 30:
                b0 += bal
            elif days <= 60:
                b31 += bal
            elif days <= 90:
                b61 += bal
            else:
                b91 += bal
        total = b0 + b31 + b61 + b91
        if total > 0:
            aging_data.append({
                'debtor': debtor,
                'bucket_0_30': b0, 'bucket_31_60': b31,
                'bucket_61_90': b61, 'bucket_90_plus': b91,
                'total': total,
            })

    return render(request, 'reports/debtor_aging.html', {'aging_data': aging_data})
