from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from apps.core.models import TimestampedModel


class PaymentMethod(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finance:payment_method_detail', kwargs={'pk': self.pk})


class ExpenseType(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finance:expense_type_detail', kwargs={'pk': self.pk})


class ExpenseItem(TimestampedModel):
    """A specific recurring expense — e.g., 'Shop Rent', 'Electricity Bill'."""
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['expense_type__name', 'name']

    def __str__(self):
        return f"{self.expense_type.name} — {self.name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finance:expense_item_detail', kwargs={'pk': self.pk})

    def current_rate(self) -> Decimal:
        """Returns the rate effective as of today."""
        rate = self.rates.filter(
            effective_from__lte=timezone.now().date()
        ).order_by('-effective_from').first()
        return rate.amount if rate else Decimal('0')


class ExpenseRate(TimestampedModel):
    """Historical rate log — rate changes are tracked, not overwritten."""
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.CASCADE, related_name='rates')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    effective_from = models.DateField()
    change_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.expense_item.name} — {self.amount} from {self.effective_from}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finance:expense_rate_detail', kwargs={'pk': self.pk})


class RecurrencePattern(TimestampedModel):
    """Defines how often an expense obligation is generated."""
    RECURRENCE_TYPES = [
        ('MONTHLY', 'Monthly'),
        ('WEEKLY', 'Weekly'),
        ('DAILY', 'Daily'),
        ('ONE_TIME', 'One Time'),
    ]
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.CASCADE, related_name='recurrences')
    recurrence_type = models.CharField(max_length=50, choices=RECURRENCE_TYPES)
    frequency_value = models.PositiveIntegerField(default=1)
    specific_day_of_week = models.IntegerField(null=True, blank=True)   # 1=Mon … 7=Sun; 0=last; negative=offset
    specific_day_of_month = models.IntegerField(default=-1)             # 1–31; 0=last; negative=offset from last
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['expense_item__name']

    def __str__(self):
        return f"{self.expense_item.name} — {self.recurrence_type}"

    def calculate_due_date(self, base_date):
        """
        Mirrors VBA CalculateDueDate() from modPayables.
        Supports last-day and negative offset conventions.
        """
        import calendar

        if self.recurrence_type == 'MONTHLY':
            last_day = calendar.monthrange(base_date.year, base_date.month)[1]
            dom = self.specific_day_of_month
            if dom is None or dom == 0:
                return base_date.replace(day=last_day)
            elif dom < 0:
                from datetime import timedelta
                return base_date.replace(day=last_day) + timedelta(days=dom)
            else:
                return base_date.replace(day=min(dom, last_day))

        elif self.recurrence_type == 'WEEKLY':
            from datetime import timedelta
            dow = self.specific_day_of_week or 1
            days_to_end_of_week = (7 - base_date.weekday()) % 7 or 7
            week_end = base_date + timedelta(days=days_to_end_of_week)
            if dow < 0:
                return week_end + timedelta(days=dow)
            return week_end

        return base_date


class PaymentObligation(TimestampedModel):
    """
    Auto-generated obligation entry for each due expense/liability period.
    Generated by management command `generate_obligations`.
    Mirrors modPayables obligation generation logic.
    """
    OBLIGATION_TYPES = [('EXPENSE', 'Expense'), ('LIABILITY', 'Liability')]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]

    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='obligations')
    liability_item = models.ForeignKey('LiabilityItem', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='obligations')
    obligation_type = models.CharField(max_length=50, choices=OBLIGATION_TYPES)
    obligation_date = models.DateField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=15, decimal_places=2)
    prepayment_applied = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"Obligation #{self.pk} — {self.due_date} — {self.amount_due}"

    @property
    def balance(self):
        return self.amount_due - self.prepayment_applied - self.amount_paid

    @property
    def payment_status(self):
        if self.balance <= 0:
            return 'PAID'
        elif self.amount_paid > 0 or self.prepayment_applied > 0:
            return 'PARTIAL'
        elif self.due_date < timezone.now().date():
            return 'OVERDUE'
        return 'PENDING'


class Payment(TimestampedModel):
    """Actual cash outflow against an obligation or directly against an expense/liability."""
    PAYMENT_TYPES = [('EXPENSE', 'Expense'), ('LIABILITY', 'Liability'), ('PREPAYMENT', 'Prepayment')]

    obligation = models.ForeignKey(PaymentObligation, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='payments')
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='payments')
    liability_item = models.ForeignKey('LiabilityItem', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='payments')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    payment_date = models.DateTimeField(default=timezone.now)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment #{self.pk} — {self.amount_paid} on {self.payment_date.date()}"


class Prepayment(TimestampedModel):
    """Advance payment that can be allocated across future obligations."""
    STATUS_CHOICES = [('Active', 'Active'), ('Exhausted', 'Exhausted'), ('Cancelled', 'Cancelled')]

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='prepayments')
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='prepayments')
    liability_item = models.ForeignKey('LiabilityItem', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='prepayments')
    total_prepaid = models.DecimalField(max_digits=15, decimal_places=2)
    amount_utilized = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    prepayment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['-prepayment_date']

    def __str__(self):
        return f"Prepayment #{self.pk} — {self.total_prepaid}"

    @property
    def amount_remaining(self):
        return self.total_prepaid - self.amount_utilized


class PaymentAllocation(TimestampedModel):
    """Links a prepayment to a specific obligation it covers."""
    prepayment = models.ForeignKey(Prepayment, on_delete=models.PROTECT, related_name='allocations')
    obligation = models.ForeignKey(PaymentObligation, on_delete=models.PROTECT, related_name='allocations')
    amount_allocated = models.DecimalField(max_digits=15, decimal_places=2)
    allocation_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-allocation_date']

    def __str__(self):
        return f"Allocation #{self.pk} — {self.amount_allocated}"


class LiabilityCategory(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Liability Categories'

    def __str__(self):
        return self.name


class LiabilityType(TimestampedModel):
    category = models.ForeignKey(LiabilityCategory, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class LiabilityItem(TimestampedModel):
    """A specific external loan or long-term liability."""
    liability_type = models.ForeignKey(LiabilityType, on_delete=models.PROTECT, related_name='items')
    name = models.CharField(max_length=255)
    original_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    maturity_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    rate = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                help_text='Interest rate (e.g., 0.12 = 12%)')
    amount_per_return = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def current_balance(self):
        paid = self.payment_details.aggregate(
            t=Coalesce(Sum('principal_amount'), Decimal('0'))
        )['t']
        return self.original_amount - paid


class LiabilityPaymentDetail(TimestampedModel):
    """Principal + interest breakdown for each liability payment."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='liability_details')
    liability_item = models.ForeignKey(LiabilityItem, on_delete=models.PROTECT,
                                        related_name='payment_details')
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Liability Payment #{self.pk} — {self.liability_item.name}"


class ObligationGeneratorLog(TimestampedModel):
    """Tracks the last time obligations were auto-generated. One row, ever."""
    last_run_date = models.DateField(unique=True)

    class Meta:
        ordering = ['-last_run_date']

    def __str__(self):
        return f"Last run: {self.last_run_date}"


# ── ExpenseType upgrades ──────────────────────────────────────────────────────

# Add is_cogs and display_order to ExpenseType via migration — done below via new fields
# (We add them as separate models to avoid touching the existing migration)

class ExpenseTypeExtra(TimestampedModel):
    """Extra fields for ExpenseType — avoids re-migrating the original model."""
    expense_type = models.OneToOneField(ExpenseType, on_delete=models.CASCADE,
                                        related_name='extra', primary_key=True)
    is_cogs = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order']


# ── Payment upgrades ──────────────────────────────────────────────────────────

class PaymentExtra(TimestampedModel):
    """Extra fields for Payment — payment_reference and approved_by."""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE,
                                   related_name='extra', primary_key=True)
    payment_reference = models.CharField(max_length=50, blank=True, db_index=True)
    approved_by = models.CharField(max_length=255, blank=True)


# ── LiabilityItem upgrades ────────────────────────────────────────────────────

class LiabilityItemExtra(TimestampedModel):
    """Extra fields for LiabilityItem — interest_type."""
    INTEREST_TYPES = [
        ('FLAT', 'Flat Rate'),
        ('REDUCING', 'Reducing Balance'),
        ('NONE', 'No Interest'),
    ]
    liability_item = models.OneToOneField(LiabilityItem, on_delete=models.CASCADE,
                                          related_name='extra', primary_key=True)
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPES, default='REDUCING')


# ── Payment Method hierarchy ──────────────────────────────────────────────────

class PaymentCategory(TimestampedModel):
    CATEGORY_CODES = [
        ('CASH', 'Physical Cash'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK', 'Bank / Cheque'),
    ]
    code = models.CharField(max_length=20, choices=CATEGORY_CODES, unique=True)
    name = models.CharField(max_length=100)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name


class PaymentProvider(TimestampedModel):
    category = models.ForeignKey(PaymentCategory, on_delete=models.PROTECT, related_name='providers')
    name = models.CharField(max_length=255, unique=True)
    short_code = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category__display_order', 'name']

    def __str__(self):
        return self.name


class PaymentMethodCategory(TimestampedModel):
    """Links existing PaymentMethod to the new PaymentCategory/Provider hierarchy."""
    payment_method = models.OneToOneField(PaymentMethod, on_delete=models.CASCADE,
                                          related_name='category_link', primary_key=True)
    category = models.ForeignKey(PaymentCategory, on_delete=models.PROTECT)
    provider = models.ForeignKey(PaymentProvider, on_delete=models.SET_NULL,
                                 null=True, blank=True)
    clears_immediately = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.payment_method.name} → {self.category.name}"


# ── Cash Register Session ─────────────────────────────────────────────────────

class CashRegisterSession(TimestampedModel):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('VARIANCE', 'Variance'),
    ]
    session_date = models.DateField(unique=True)
    opened_by = models.CharField(max_length=255)
    closed_by = models.CharField(max_length=255, blank=True)
    opening_float = models.DecimalField(max_digits=15, decimal_places=2)
    variance_explanation = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    class Meta:
        ordering = ['-session_date']

    def __str__(self):
        return f"Session {self.session_date} [{self.status}]"

    def closing_balance_for(self, category_code: str) -> Decimal:
        return self.balances.filter(
            payment_method_link__category__code=category_code,
            payment_method_link__clears_immediately=True
        ).aggregate(
            t=Coalesce(Sum('physical_closing_balance'), Decimal('0'))
        )['t']


class SessionBalance(TimestampedModel):
    session = models.ForeignKey(CashRegisterSession, on_delete=models.CASCADE, related_name='balances')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    physical_closing_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    system_expected_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    uncleared_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        unique_together = [['session', 'payment_method']]

    @property
    def variance_amount(self):
        return self.system_expected_balance - (self.physical_closing_balance - self.uncleared_amount)

    def __str__(self):
        return f"{self.session.session_date} | {self.payment_method.name}"


# ── Budget ────────────────────────────────────────────────────────────────────

class BudgetLine(TimestampedModel):
    BUDGET_TYPES = [
        ('REVENUE', 'Net Sales Revenue'),
        ('COGS', 'Cost of Goods Sold'),
        ('EXPENSE', 'Operating Expense'),
    ]
    financial_year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField(help_text='1=January … 12=December')
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='budget_lines')
    description = models.CharField(max_length=255, blank=True)
    budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = [['financial_year', 'month', 'budget_type', 'expense_type']]
        ordering = ['financial_year', 'month', 'budget_type']

    def __str__(self):
        return f"{self.financial_year}/{self.month:02d} — {self.get_budget_type_display()} — TZS {self.budgeted_amount:,.0f}"
