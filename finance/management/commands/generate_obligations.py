from django.core.management.base import BaseCommand
from datetime import date
from finance.services import _run_generation


class Command(BaseCommand):
    help = 'Generate payment obligations from active recurrence patterns'

    def add_arguments(self, parser):
        parser.add_argument('--months', type=int, default=2)
        parser.add_argument('--from-date', type=str, default=None)

    def handle(self, *args, **options):
        from_date = date.fromisoformat(options['from_date']) if options['from_date'] else date.today()
        _run_generation(from_date, months_ahead=options['months'])
        self.stdout.write(self.style.SUCCESS('Obligations generated successfully.'))
