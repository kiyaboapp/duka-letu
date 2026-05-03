"""
finance/services.py — auto_generate_obligations()
Idempotent: runs at most once per calendar day.
Safe to call on every Finance page load.
"""
from datetime import date, timedelta
import calendar
from .models import ObligationGeneratorLog, RecurrencePattern, PaymentObligation


def auto_generate_obligations():
    today = date.today()
    if ObligationGeneratorLog.objects.filter(last_run_date=today).exists():
        return
    _run_generation(today, months_ahead=2)
    ObligationGeneratorLog.objects.get_or_create(last_run_date=today)


def _run_generation(from_date, months_ahead=2):
    end_month = from_date.month + months_ahead - 1
    end_year = from_date.year + (end_month - 1) // 12
    end_month = ((end_month - 1) % 12) + 1
    last_day = calendar.monthrange(end_year, end_month)[1]
    to_date = date(end_year, end_month, last_day)

    patterns = RecurrencePattern.objects.filter(
        is_active=True,
        expense_item__is_active=True,
        start_date__lte=to_date,
    ).exclude(end_date__lt=from_date).select_related('expense_item')

    for pattern in patterns:
        _generate_for_pattern(pattern, from_date, to_date)


def _generate_for_pattern(pattern, from_date, to_date):
    current = pattern.start_date if pattern.start_date > from_date else from_date
    while current <= to_date:
        due_date = pattern.calculate_due_date(current)
        amount = pattern.expense_item.current_rate()
        if amount > 0 and not PaymentObligation.objects.filter(
            expense_item=pattern.expense_item,
            due_date=due_date,
            obligation_type='EXPENSE',
        ).exists():
            PaymentObligation.objects.create(
                expense_item=pattern.expense_item,
                obligation_type='EXPENSE',
                obligation_date=current,
                due_date=due_date,
                amount_due=amount,
                description=f'Auto: {pattern.expense_item.name}',
            )
        if pattern.recurrence_type == 'MONTHLY':
            month = current.month + 1
            year = current.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            current = date(year, month, 1)
        elif pattern.recurrence_type == 'WEEKLY':
            current += timedelta(weeks=pattern.frequency_value)
        elif pattern.recurrence_type == 'DAILY':
            current += timedelta(days=pattern.frequency_value)
        else:
            break
