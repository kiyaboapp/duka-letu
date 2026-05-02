"""
Management command: import_access
Imports data from the exported Access database JSON (access_data.json)
into the Django models, preserving original PKs for FK integrity.

Usage:
    python manage.py import_access
    python manage.py import_access --path /custom/path/access_data.json
    python manage.py import_access --clear   # wipe existing data first
"""

import json
from decimal import Decimal
from datetime import datetime, date
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction


def _d(val):
    """Convert value to Decimal or None."""
    if val is None:
        return None
    return Decimal(str(val))


def _dt(val):
    """Parse ISO datetime string to timezone-aware datetime or None."""
    if not val:
        return None
    import datetime as dt_module
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            naive = datetime.strptime(val[:19], fmt)
            return naive.replace(tzinfo=dt_module.timezone.utc)
        except ValueError:
            continue
    return None


def _date(val):
    """Parse ISO date string to date or None."""
    dt = _dt(val)
    return dt.date() if dt else None


class Command(BaseCommand):
    help = 'Import Access database export (access_data.json) into Django models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path', default='access_data.json',
            help='Path to access_data.json (default: access_data.json in project root)'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing data before importing (use with caution)'
        )

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.is_absolute():
            from django.conf import settings
            base = Path(settings.BASE_DIR) if hasattr(settings, 'BASE_DIR') else Path(__file__).resolve().parents[3]
            path = base / options['path']

        self.stdout.write(f'Loading data from {path}')
        with open(path, encoding='utf-8') as f:
            data = json.load(f)

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self._clear_all()

        with transaction.atomic():
            self._import(data)

        self.stdout.write(self.style.SUCCESS('Import complete.'))

    # ------------------------------------------------------------------
    def _clear_all(self):
        from assets.models import Asset, AssetType, AssetCategory
        from catalog.models import (Category, ProductType, Brand, Unit,
                                     Spec, SpecValue, Product, ProductSpec)
        from inventory.models import Supplier, Purchase, PurchaseDetail, ReturnOutward
        from sales.models import (Sale, ReturnInward, OfficeUseCategory,
                                   SaleOfficeUse, DrawingCategory, Drawing)
        from finance.models import (PaymentMethod, ExpenseType, ExpenseItem,
                                     ExpenseRate, RecurrencePattern,
                                     PaymentObligation, Payment, Prepayment,
                                     PaymentAllocation, LiabilityCategory,
                                     LiabilityType, LiabilityItem,
                                     LiabilityPaymentDetail)
        from credit.models import Debtor, Debt, DebtReturn

        for m in [
            Asset, AssetType, AssetCategory,
            LiabilityPaymentDetail, PaymentAllocation, Prepayment,
            Payment, PaymentObligation, RecurrencePattern,
            LiabilityItem, LiabilityType, LiabilityCategory,
            DebtReturn, Debt, Debtor,
            Drawing, DrawingCategory, SaleOfficeUse, OfficeUseCategory,
            ReturnInward, ReturnOutward, PurchaseDetail,
            Sale, Purchase, Supplier,
            ProductSpec, Product, SpecValue, Spec,
            Brand, Unit, ProductType, Category,
            ExpenseRate, ExpenseItem, ExpenseType, PaymentMethod,
        ]:
            m.objects.all().delete()

    # ------------------------------------------------------------------
    def _import(self, data):
        self._catalog(data)
        self._assets(data)
        self._inventory(data)
        self._finance(data)
        self._sales(data)
        self._credit(data)

    # ------------------------------------------------------------------
    def _catalog(self, data):
        from catalog.models import (Category, ProductType, Brand, Unit,
                                     Spec, SpecValue, Product, ProductSpec)

        self.stdout.write('  catalog...')

        for r in data['tbl_categories']:
            Category.objects.update_or_create(
                pk=r['category_id'],
                defaults={'name': r['category_name']}
            )

        for r in data['tbl_types']:
            ProductType.objects.update_or_create(
                pk=r['type_id'],
                defaults={
                    'category_id': r['category_id'],
                    'name': r['type_name'],
                }
            )

        for r in data['tbl_brands']:
            Brand.objects.update_or_create(
                pk=r['brand_id'],
                defaults={'name': r['brand_name']}
            )

        for r in data['tbl_units']:
            Unit.objects.update_or_create(
                pk=r['unit_id'],
                defaults={
                    'name': r['unit_name'],
                    'abbreviation': r.get('unit_abbr') or '',
                }
            )

        for r in data['tbl_specs']:
            Spec.objects.update_or_create(
                pk=r['spec_id'],
                defaults={'name': r['spec_name']}
            )

        for r in data['tbl_spec_values']:
            SpecValue.objects.update_or_create(
                pk=r['spec_value_id'],
                defaults={
                    'spec_id': r['spec_id'],
                    'value': r['spec_value'],
                }
            )

        for r in data['tbl_products']:
            Product.objects.update_or_create(
                pk=r['product_id'],
                defaults={
                    'name': r['product_name'],
                    'product_type_id': r['type_id'],
                    'brand_id': r.get('brand_id'),
                    'unit_id': r.get('unit_id'),
                    'image_path': r.get('path') or '',
                }
            )

        for r in data['tbl_product_specs']:
            ProductSpec.objects.update_or_create(
                pk=r['product_spec_id'],
                defaults={
                    'product_id': r['product_id'],
                    'spec_value_id': r['spec_value_id'],
                    'default_cost_price': _d(r.get('default_cost_price')),
                    'default_selling_price': _d(r.get('default_selling_price')),
                    'reorder_level': r.get('reorder_level') or 5,
                    'current_stock': r.get('current_stock') or 0,
                }
            )

        self.stdout.write(self.style.SUCCESS('    catalog done'))

    # ------------------------------------------------------------------
    def _assets(self, data):
        from assets.models import AssetCategory, AssetType, Asset

        self.stdout.write('  assets...')

        for r in data['tbl_asset_categories']:
            AssetCategory.objects.update_or_create(
                pk=r['asset_category_id'],
                defaults={'name': r['asset_category']}
            )

        for r in data['tbl_asset_types']:
            AssetType.objects.update_or_create(
                pk=r['asset_type_id'],
                defaults={
                    'category_id': r['asset_category_id'],
                    'name': r['asset_type_name'],
                }
            )

        for r in data['tbl_assets']:
            Asset.objects.update_or_create(
                pk=r['asset_id'],
                defaults={
                    'asset_type_id': r['asset_type_id'],
                    'name': r['asset_name'],
                    'worth': _d(r['asset_worth']),
                    'notes': r.get('notes') or '',
                    'date_checked': _dt(r.get('date_checked')) or datetime.now(),
                }
            )

        self.stdout.write(self.style.SUCCESS('    assets done'))

    # ------------------------------------------------------------------
    def _inventory(self, data):
        from inventory.models import Supplier, Purchase, PurchaseDetail, ReturnOutward

        self.stdout.write('  inventory...')

        for r in data['tbl_suppliers']:
            Supplier.objects.update_or_create(
                pk=r['supplier_id'],
                defaults={
                    'name': r['supplier_name'],
                    'contact_person': r.get('contact_person') or '',
                    'phone': r.get('phone') or '',
                    'address': r.get('address') or '',
                }
            )

        for r in data['tbl_purchases']:
            Purchase.objects.update_or_create(
                pk=r['purchase_id'],
                defaults={
                    'supplier_id': r['supplier_id'],
                    'purchase_date': _dt(r['purchase_date']) or datetime.now(),
                    'invoice_number': r.get('invoice_number') or '',
                }
            )

        for r in data['tbl_purchase_details']:
            PurchaseDetail.objects.update_or_create(
                pk=r['purchase_detail_id'],
                defaults={
                    'purchase_id': r['purchase_id'],
                    'product_spec_id': r['product_spec_id'],
                    'quantity': r['quantity'],
                    'unit_cost': _d(r['unit_cost']),
                    'suggested_selling_price': _d(r.get('suggested_selling_price')),
                }
            )

        for r in data['tbl_return_outwards']:
            ReturnOutward.objects.update_or_create(
                pk=r['return_outward_id'],
                defaults={
                    'purchase_detail_id': r['purchase_detail_id'],
                    'quantity': r['quantity'],
                    'unit_price': _d(r['unit_price']),
                    'reason': r.get('reason') or '',
                    'sale_date': _dt(r.get('sale_date')) or datetime.now(),
                }
            )

        self.stdout.write(self.style.SUCCESS('    inventory done'))

    # ------------------------------------------------------------------
    def _finance(self, data):
        from finance.models import (
            PaymentMethod, ExpenseType, ExpenseItem, ExpenseRate,
            RecurrencePattern, PaymentObligation, Payment, Prepayment,
            PaymentAllocation, LiabilityCategory, LiabilityType,
            LiabilityItem, LiabilityPaymentDetail,
        )

        self.stdout.write('  finance...')

        for r in data['tbl_payment_methods']:
            PaymentMethod.objects.update_or_create(
                pk=r['payment_method_id'],
                defaults={'name': r['payment_method']}
            )

        for r in data['tbl_expense_types']:
            ExpenseType.objects.update_or_create(
                pk=r['expense_type_id'],
                defaults={'name': r['expense_type']}
            )

        for r in data['tbl_expense_items']:
            ExpenseItem.objects.update_or_create(
                pk=r['expense_item_id'],
                defaults={
                    'expense_type_id': r['expense_type_id'],
                    'name': r['item_name'],
                    'description': r.get('item_description') or '',
                    'start_date': _date(r['start_date']) or date.today(),
                    'end_date': _date(r.get('end_date')),
                    'is_active': bool(r.get('is_active', True)),
                }
            )

        for r in data['tbl_expense_rates']:
            ExpenseRate.objects.update_or_create(
                pk=r['rate_id'],
                defaults={
                    'expense_item_id': r['expense_item_id'],
                    'amount': _d(r['rate_amount']),
                    'effective_from': _date(r['effective_from']) or date.today(),
                    'change_reason': r.get('change_reason') or '',
                }
            )

        for r in data['tbl_recurrence_patterns']:
            RecurrencePattern.objects.update_or_create(
                pk=r['recurrence_id'],
                defaults={
                    'expense_item_id': r['expense_item_id'],
                    'recurrence_type': r.get('recurrence_type') or 'MONTHLY',
                    'frequency_value': r.get('frequency_value') or 1,
                    'specific_day_of_week': r.get('specific_day_of_week'),
                    'specific_day_of_month': r.get('specific_day_of_month') or -1,
                    'start_date': _date(r['start_date']) or date.today(),
                    'end_date': _date(r.get('end_date')),
                    'is_active': bool(r.get('is_active', True)),
                }
            )

        for r in data['tbl_liability_categories']:
            LiabilityCategory.objects.update_or_create(
                pk=r['liability_category_id'],
                defaults={'name': r['liability_category']}
            )

        for r in data['tbl_liability_types']:
            LiabilityType.objects.update_or_create(
                pk=r['liability_type_id'],
                defaults={
                    'category_id': r['liability_category_id'],
                    'name': r['liability_type_name'],
                }
            )

        for r in data['tbl_liability_items']:
            LiabilityItem.objects.update_or_create(
                pk=r['liability_item_id'],
                defaults={
                    'liability_type_id': r['liability_type_id'],
                    'name': r['liability_name'],
                    'original_amount': _d(r['original_amount']),
                    'start_date': _date(r['start_date']) or date.today(),
                    'maturity_date': _date(r.get('maturity_date')),
                    'is_active': bool(r.get('is_active', True)),
                    'rate': _d(r.get('rate')),
                    'amount_per_return': _d(r.get('amount_per_return')),
                }
            )

        for r in data['tbl_payment_obligations']:
            PaymentObligation.objects.update_or_create(
                pk=r['obligation_id'],
                defaults={
                    'expense_item_id': r.get('expense_item_id'),
                    'liability_item_id': r.get('liability_item_id'),
                    'obligation_type': r.get('obligation_type') or 'EXPENSE',
                    'obligation_date': _date(r['obligation_date']) or date.today(),
                    'due_date': _date(r['due_date']) or date.today(),
                    'amount_due': _d(r['amount_due']),
                    'prepayment_applied': _d(r.get('prepayment_applied')) or Decimal('0'),
                    'amount_paid': _d(r.get('amount_paid')) or Decimal('0'),
                    'description': r.get('description') or '',
                }
            )

        for r in data['tbl_payments']:
            Payment.objects.update_or_create(
                pk=r['payment_id'],
                defaults={
                    'obligation_id': r.get('obligation_id'),
                    'expense_item_id': r.get('expense_item_id'),
                    'liability_item_id': r.get('liability_item_id'),
                    'payment_type': r.get('payment_type') or 'EXPENSE',
                    'payment_date': _dt(r['payment_date']) or datetime.now(),
                    'amount_paid': _d(r['amount_paid']),
                    'payment_method_id': r['payment_method'],
                    'reference_number': r.get('reference_number') or '',
                    'description': r.get('description') or '',
                }
            )

        for r in data['tbl_prepayments']:
            Prepayment.objects.update_or_create(
                pk=r['prepayment_id'],
                defaults={
                    'payment_id': r['payment_id'],
                    'expense_item_id': r.get('expense_item_id'),
                    'liability_item_id': r.get('liability_item_id'),
                    'total_prepaid': _d(r['total_prepaid']),
                    'amount_utilized': _d(r.get('amount_utilized')) or Decimal('0'),
                    'prepayment_date': _dt(r.get('prepayment_date')) or datetime.now(),
                    'status': r.get('status') or 'Active',
                }
            )

        for r in data['tbl_payment_allocations']:
            PaymentAllocation.objects.update_or_create(
                pk=r['allocation_id'],
                defaults={
                    'prepayment_id': r['prepayment_id'],
                    'obligation_id': r['obligation_id'],
                    'amount_allocated': _d(r['amount_allocated']),
                    'allocation_date': _dt(r.get('allocation_date')) or datetime.now(),
                }
            )

        for r in data['tbl_liability_payment_details']:
            LiabilityPaymentDetail.objects.update_or_create(
                pk=r['detail_id'],
                defaults={
                    'payment_id': r['payment_id'],
                    'liability_item_id': r['liability_item_id'],
                    'principal_amount': _d(r['principal_amount']),
                    'interest_amount': _d(r['interest_amount']),
                    'balance_after_payment': _d(r.get('balance_after_payment')),
                    'payment_date': _dt(r.get('payment_date')) or datetime.now(),
                }
            )

        self.stdout.write(self.style.SUCCESS('    finance done'))

    # ------------------------------------------------------------------
    def _sales(self, data):
        from sales.models import (Sale, ReturnInward, OfficeUseCategory,
                                   SaleOfficeUse, DrawingCategory, Drawing)

        self.stdout.write('  sales...')

        for r in data['tbl_drawing_categories']:
            DrawingCategory.objects.update_or_create(
                pk=r['drawing_category_id'],
                defaults={
                    'name': r['drawing_category'],
                    'notes': r.get('notes') or '',
                }
            )

        # office_use categories
        for r in data['tbl_office_use']:
            OfficeUseCategory.objects.update_or_create(
                pk=r['office_use_id'],
                defaults={'name': r['office_use']}
            )

        for r in data['tbl_sales']:
            Sale.objects.update_or_create(
                pk=r['sale_id'],
                defaults={
                    'product_spec_id': r['product_spec_id'],
                    'quantity': r['quantity'],
                    'unit_price': _d(r['unit_price']),
                    'discount': _d(r.get('discount')) or Decimal('0'),
                    'sale_date': _dt(r['sale_date']) or datetime.now(),
                    'payment_method_id': r.get('payment_method_id'),
                    'notes': r.get('notes') or '',
                }
            )

        for r in data['tbl_return_inwards']:
            ReturnInward.objects.update_or_create(
                pk=r['return_inward_id'],
                defaults={
                    'sale_id': r['sale_id'],
                    'quantity': r['quantity'],
                    'unit_price': _d(r['unit_price']),
                    'reason': r.get('reason') or '',
                    'sale_date': _dt(r.get('sale_date')) or datetime.now(),
                }
            )

        for r in data['tbl_sales_office_use']:
            SaleOfficeUse.objects.update_or_create(
                pk=r['sale_id'],
                defaults={
                    'product_spec_id': r['product_spec_id'],
                    'original_sale_id': r.get('sales_sale_id'),
                    'office_use_category_id': r.get('office_use_id'),
                    'quantity': r['quantity'],
                    'unit_price': _d(r['unit_price']),
                    'discount': _d(r.get('discount')) or Decimal('0'),
                    'sale_date': _dt(r['sale_date']) or datetime.now(),
                    'reason': r.get('reason') or '',
                }
            )

        for r in data['tbl_drawings']:
            Drawing.objects.update_or_create(
                pk=r['drawing_id'],
                defaults={
                    'drawing_category_id': r['drawing_category_id'],
                    'product_spec_id': r['product_spec_id'],
                    'quantity': r['quantity'],
                    'unit_price': _d(r['unit_price']),
                    'discount': _d(r.get('discount')) or Decimal('0'),
                    'sale_date': _dt(r['sale_date']) or datetime.now(),
                    'notes': r.get('notes') or '',
                }
            )

        self.stdout.write(self.style.SUCCESS('    sales done'))

    # ------------------------------------------------------------------
    def _credit(self, data):
        from credit.models import Debtor, Debt, DebtReturn

        self.stdout.write('  credit...')

        for r in data['tbl_debtors']:
            Debtor.objects.update_or_create(
                pk=r['debtor_id'],
                defaults={
                    'name': r['debtor_name'],
                    'address': r.get('debtor_address') or '',
                    'phone_1': r.get('phone_number_1') or '',
                    'phone_2': r.get('phone_number_2') or '',
                    'nida_id': r.get('nida_id') or '',
                }
            )

        for r in data['tbl_debts']:
            Debt.objects.update_or_create(
                pk=r['sale_id'],
                defaults={
                    'debtor_id': r['debtor_id'],
                    'product_spec_id': r['product_spec_id'],
                    'quantity': r['quantity'],
                    'unit_price': _d(r['unit_price']),
                    'discount': _d(r.get('discount')) or Decimal('0'),
                    'sale_date': _dt(r['sale_date']) or datetime.now(),
                    'expected_payment_date': _date(r.get('expected_payment_date')),
                }
            )

        for r in data['tbl_debt_returns']:
            DebtReturn.objects.update_or_create(
                pk=r['debt_return_id'],
                defaults={
                    'debt_id': r['debt_id'],
                    'amount': _d(r['amount']),
                    'return_date': _dt(r['return_date']) or datetime.now(),
                    'payment_method_id': r['payment_method_id'],
                    'comment': r.get('comment') or '',
                }
            )

        self.stdout.write(self.style.SUCCESS('    credit done'))
