from django.core.management.base import BaseCommand
from finance.models import PaymentCategory, PaymentProvider, PaymentMethod, PaymentMethodCategory

CATEGORIES = [
    ('CASH', 'Cash', 0),
    ('MOBILE_MONEY', 'Mobile Money', 1),
    ('BANK', 'Bank', 2),
]

PROVIDERS = [
    ('Vodacom', 'MOBILE_MONEY', 'VOD'),
    ('Tigo', 'MOBILE_MONEY', 'TIGO'),
    ('Airtel', 'MOBILE_MONEY', 'AIR'),
    ('Halopesa', 'MOBILE_MONEY', 'HALO'),
    ('CRDB Bank', 'BANK', 'CRDB'),
    ('NMB Bank', 'BANK', 'NMB'),
    ('NBC Bank', 'BANK', 'NBC'),
]

# (method_name, category_code, provider_name_or_None, clears_immediately)
METHODS = [
    ('Cash', 'CASH', None, True),
    ('M-Pesa', 'MOBILE_MONEY', 'Vodacom', True),
    ('Tigo Pesa', 'MOBILE_MONEY', 'Tigo', True),
    ('Airtel Money', 'MOBILE_MONEY', 'Airtel', True),
    ('Halopesa', 'MOBILE_MONEY', 'Halopesa', True),
    ('CRDB Direct Transfer', 'BANK', 'CRDB Bank', True),
    ('CRDB Cheque', 'BANK', 'CRDB Bank', False),
    ('NMB Direct Transfer', 'BANK', 'NMB Bank', True),
    ('NMB Cheque', 'BANK', 'NMB Bank', False),
    ('NBC Direct Transfer', 'BANK', 'NBC Bank', True),
]

# Map existing DB payment method names to new categories
EXISTING_MAP = {
    'Cash': ('CASH', None, True),
    'Mobile Payments': ('MOBILE_MONEY', 'Vodacom', True),
    'Bank (Cheque)': ('BANK', 'CRDB Bank', False),
    'Cheque': ('BANK', 'CRDB Bank', False),
}


class Command(BaseCommand):
    help = 'Seed payment categories, providers, and method links.'

    def handle(self, *args, **options):
        cat_map = {}
        for code, name, order in CATEGORIES:
            cat, _ = PaymentCategory.objects.update_or_create(
                code=code, defaults={'name': name, 'display_order': order}
            )
            cat_map[code] = cat
            self.stdout.write(f'  Category: {cat}')

        prov_map = {}
        for pname, cat_code, short in PROVIDERS:
            prov, _ = PaymentProvider.objects.update_or_create(
                name=pname, defaults={'category': cat_map[cat_code], 'short_code': short}
            )
            prov_map[pname] = prov
            self.stdout.write(f'  Provider: {prov}')

        # Create new PaymentMethod records for new methods
        for mname, cat_code, prov_name, clears in METHODS:
            method, created = PaymentMethod.objects.get_or_create(name=mname)
            provider = prov_map.get(prov_name) if prov_name else None
            PaymentMethodCategory.objects.update_or_create(
                payment_method=method,
                defaults={
                    'category': cat_map[cat_code],
                    'provider': provider,
                    'clears_immediately': clears,
                }
            )
            self.stdout.write(f'  {"Created" if created else "Linked"}: {mname}')

        # Link existing 4 payment methods
        for mname, (cat_code, prov_name, clears) in EXISTING_MAP.items():
            try:
                method = PaymentMethod.objects.get(name=mname)
                provider = prov_map.get(prov_name) if prov_name else None
                PaymentMethodCategory.objects.update_or_create(
                    payment_method=method,
                    defaults={
                        'category': cat_map[cat_code],
                        'provider': provider,
                        'clears_immediately': clears,
                    }
                )
                self.stdout.write(f'  Linked existing: {mname}')
            except PaymentMethod.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS('Payment method seed complete.'))
