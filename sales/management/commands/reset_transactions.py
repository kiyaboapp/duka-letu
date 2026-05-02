from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'DANGER: Delete all transaction data. Preserves master/setup data.'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true',
                            help='Required flag to actually run')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stderr.write('Dry run. Pass --confirm to actually delete.')
            return

        self.stdout.write(self.style.WARNING('Deleting all transactions...'))

        with transaction.atomic():
            from credit.models import DebtReturn, Debt
            from sales.models import ReturnInward, SaleOfficeUse, Drawing, Sale
            from inventory.models import ReturnOutward, PurchaseDetail, Purchase
            from finance.models import (
                PaymentAllocation, LiabilityPaymentDetail,
                Prepayment, Payment, PaymentObligation
            )
            from catalog.models import ProductSpec

            DebtReturn.objects.all().delete()
            ReturnInward.objects.all().delete()
            ReturnOutward.objects.all().delete()
            SaleOfficeUse.objects.all().delete()
            Drawing.objects.all().delete()
            Debt.objects.all().delete()
            Sale.objects.all().delete()
            PurchaseDetail.objects.all().delete()
            Purchase.objects.all().delete()
            PaymentAllocation.objects.all().delete()
            LiabilityPaymentDetail.objects.all().delete()
            Prepayment.objects.all().delete()
            Payment.objects.all().delete()
            PaymentObligation.objects.all().delete()

            ProductSpec.objects.all().update(current_stock=0)

        self.stdout.write(self.style.SUCCESS('Done. All transactions deleted.'))
