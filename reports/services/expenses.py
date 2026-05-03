from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce
from finance.models import Payment, PaymentObligation


class ExpenseService:
    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end

    def _payments(self):
        return Payment.objects.filter(
            payment_date__date__range=(self.start, self.end),
            payment_type='EXPENSE',
            expense_item__isnull=False,
        )

    def by_type(self):
        return list(
            self._payments()
            .values('expense_item__expense_type__name', 'expense_item__expense_type__id')
            .annotate(total=Coalesce(Sum('amount_paid'), Decimal('0')))
            .order_by('expense_item__expense_type__name')
        )

    def by_item(self):
        return list(
            self._payments()
            .values('expense_item__id', 'expense_item__name', 'expense_item__expense_type__name')
            .annotate(total=Coalesce(Sum('amount_paid'), Decimal('0')))
            .order_by('expense_item__expense_type__name', 'expense_item__name')
        )

    def total(self) -> Decimal:
        return Payment.objects.filter(
            payment_date__date__range=(self.start, self.end),
            payment_type='EXPENSE',
        ).aggregate(t=Coalesce(Sum('amount_paid'), Decimal('0')))['t']

    def obligations_summary(self):
        agg = PaymentObligation.objects.filter(
            due_date__range=(self.start, self.end)
        ).aggregate(
            total_due=Coalesce(Sum('amount_due'), Decimal('0')),
            total_paid=Coalesce(Sum('amount_paid'), Decimal('0')),
            total_prepaid=Coalesce(Sum('prepayment_applied'), Decimal('0')),
        )
        return {
            'total_due': agg['total_due'],
            'total_paid': agg['total_paid'],
            'total_prepaid': agg['total_prepaid'],
            'outstanding': agg['total_due'] - agg['total_paid'] - agg['total_prepaid'],
        }
