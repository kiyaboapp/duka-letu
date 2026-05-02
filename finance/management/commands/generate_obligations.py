from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import calendar
from finance.models import RecurrencePattern, PaymentObligation, ExpenseItem


class Command(BaseCommand):
    help = 'Generate payment obligations from active recurrence patterns'

    def add_arguments(self, parser):
        parser.add_argument('--months', type=int, default=1,
                            help='Number of months ahead to generate (default: 1)')
        parser.add_argument('--from-date', type=str, default=None,
                            help='Start date YYYY-MM-DD (default: today)')

    def handle(self, *args, **options):
        from_date = date.today()
        if options['from_date']:
            from_date = date.fromisoformat(options['from_date'])

        months_ahead = options['months']
        # Compute end date
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

        created = 0
        for pattern in patterns:
            obligations = self._generate_for_pattern(pattern, from_date, to_date)
            created += len(obligations)

        self.stdout.write(self.style.SUCCESS(
            f'Generated {created} payment obligations up to {to_date}'
        ))

    def _generate_for_pattern(self, pattern, from_date, to_date):
        created = []
        current = pattern.start_date if pattern.start_date > from_date else from_date

        while current <= to_date:
            due_date = pattern.calculate_due_date(current)
            amount = pattern.expense_item.current_rate()

            # Skip if already exists (idempotent)
            exists = PaymentObligation.objects.filter(
                expense_item=pattern.expense_item,
                due_date=due_date,
                obligation_type='EXPENSE',
            ).exists()

            if not exists and amount > 0:
                obj = PaymentObligation.objects.create(
                    expense_item=pattern.expense_item,
                    obligation_type='EXPENSE',
                    obligation_date=current,
                    due_date=due_date,
                    amount_due=amount,
                    description=f'Auto-generated: {pattern.expense_item.name}',
                )
                created.append(obj)

            # Advance to next period
            if pattern.recurrence_type == 'MONTHLY':
                # Add one month
                month = current.month + 1
                year = current.year + (month - 1) // 12
                month = ((month - 1) % 12) + 1
                current = date(year, month, 1)
            elif pattern.recurrence_type == 'WEEKLY':
                current += timedelta(weeks=pattern.frequency_value)
            elif pattern.recurrence_type == 'DAILY':
                current += timedelta(days=pattern.frequency_value)
            else:
                break  # ONE_TIME

        return created
