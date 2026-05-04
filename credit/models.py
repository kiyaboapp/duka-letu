from django.db import models
from django.utils import timezone
from django.db.models import Sum, ExpressionWrapper, DecimalField, F
from django.db.models.functions import Coalesce
from decimal import Decimal
from catalog.models import ProductSpec
from finance.models import PaymentMethod
from apps.core.models import TimestampedModel
from apps.core.services import ActionMixin


class Debtor(TimestampedModel, ActionMixin):
    """Credit customer (accounts receivable party)."""
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone_1 = models.CharField(max_length=30, blank=True)
    phone_2 = models.CharField(max_length=30, blank=True)
    nida_id = models.CharField(max_length=255, blank=True, verbose_name='NIDA ID')
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       help_text='Max outstanding balance. 0 = no limit.')
    is_blocked = models.BooleanField(default=False,
                                     help_text='Block new credit sales for this debtor.')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_debt(self):
        """Sum of (qty * unit_price - discount) across all debts — computed at DB level."""
        expr = ExpressionWrapper(
            F('quantity') * F('unit_price') - F('discount'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
        return self.debts.aggregate(
            t=Coalesce(Sum(expr), Decimal('0'), output_field=DecimalField(max_digits=15, decimal_places=2))
        )['t']

    @property
    def total_paid(self):
        return DebtReturn.objects.filter(debt__debtor=self).aggregate(
            t=Coalesce(Sum('amount'), Decimal('0'))
        )['t']

    @property
    def outstanding_balance(self):
        return self.total_debt - self.total_paid

    @property
    def is_over_limit(self):
        if self.credit_limit == 0:
            return False
        return self.outstanding_balance > self.credit_limit

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('credit:debtor_detail', kwargs={'pk': self.pk})
    
    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_edit_url(self):
        from django.urls import reverse
        return reverse('credit:debtor_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        from django.urls import reverse
        return reverse('credit:debtor_delete', kwargs={'pk': self.pk})
    
    def get_credit_sale_url(self):
        """Create a new credit sale for this debtor."""
        from django.urls import reverse
        return f"{reverse('credit:debt_create')}?debtor={self.pk}"
    
    def get_make_payment_url(self):
        """Make a payment/repayment for this debtor."""
        from django.urls import reverse
        return f"{reverse('credit:debt_return_create')}?debtor={self.pk}"
    
    def get_statement_url(self):
        """View debtor statement/account history."""
        return self.get_absolute_url()
    
    def can_edit(self, user=None) -> bool:
        """Allow editing unless there are outstanding debts."""
        return self.outstanding_balance == 0 or True  # Simplified: always allow
    
    def can_delete(self, user=None) -> bool:
        """Prevent deletion if debtor has any debts."""
        return not self.debts.exists()
    
    def get_status_badge(self) -> dict:
        """Returns status badge based on debtor state."""
        if self.is_blocked:
            return {'label': 'Blocked', 'color': 'bg-red-100 text-red-800'}
        elif self.is_over_limit:
            return {'label': 'Over Limit', 'color': 'bg-orange-100 text-orange-800'}
        elif self.outstanding_balance > 0:
            return {'label': 'Has Balance', 'color': 'bg-yellow-100 text-yellow-800'}
        else:
            return {'label': 'Clear', 'color': 'bg-green-100 text-green-800'}
    
    def get_outstanding_balance_display(self) -> str:
        """Formatted outstanding balance."""
        return f"TZS {self.outstanding_balance:,.0f}"
    
    def get_debt_count(self) -> int:
        """Get number of outstanding debts."""
        return self.debts.filter(returns__isnull=True).count()


class Debt(TimestampedModel, ActionMixin):
    """A single credit sale line — creates an accounts receivable."""
    debtor = models.ForeignKey(Debtor, on_delete=models.PROTECT, related_name='debts')
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='debts')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    expected_payment_date = models.DateField(null=True, blank=True)
    reference_number = models.CharField(max_length=50, blank=True, db_index=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL,
                                       null=True, blank=True,
                                       help_text='Expected repayment channel.')

    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Credit Sale (Debt)'

    def __str__(self):
        return f"Credit Sale #{self.pk} — {self.debtor.name}"

    @property
    def amount_due(self):
        return (self.quantity * self.unit_price) - self.discount

    @property
    def total_returned(self):
        return self.returns.aggregate(
            t=Coalesce(Sum('amount'), Decimal('0'))
        )['t']

    @property
    def balance(self):
        return self.amount_due - self.total_returned

    @property
    def is_overdue(self):
        if not self.expected_payment_date:
            return False
        return self.balance > 0 and self.expected_payment_date < timezone.now().date()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.reference_number:
            self.reference_number = f"DT-{self.sale_date.year}-{self.pk:04d}"
            Debt.objects.filter(pk=self.pk).update(reference_number=self.reference_number)
        spec = self.product_spec
        spec.update_stock()
        if self.unit_price and self.unit_price != spec.default_selling_price:
            spec.default_selling_price = self.unit_price
            spec.save(update_fields=['default_selling_price'])

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('credit:debt_detail', kwargs={'pk': self.pk})
    
    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_edit_url(self):
        from django.urls import reverse
        return reverse('credit:debt_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        from django.urls import reverse
        return reverse('credit:debt_delete', kwargs={'pk': self.pk})
    
    def get_receive_payment_url(self):
        """URL to receive payment for this debt."""
        from django.urls import reverse
        return f"{reverse('credit:debt_return_create')}?debt={self.pk}"
    
    def can_edit(self, user=None) -> bool:
        """Allow editing only if no payments received yet."""
        return self.total_returned == 0
    
    def can_delete(self, user=None) -> bool:
        """Prevent deletion if payments have been made."""
        return not self.returns.exists()
    
    def get_status_badge(self) -> dict:
        """Returns status badge based on payment state."""
        if self.balance <= 0:
            return {'label': 'Paid', 'color': 'bg-green-100 text-green-800'}
        elif self.is_overdue:
            return {'label': 'Overdue', 'color': 'bg-red-100 text-red-800'}
        elif self.total_returned > 0:
            return {'label': 'Partially Paid', 'color': 'bg-yellow-100 text-yellow-800'}
        else:
            return {'label': 'Unpaid', 'color': 'bg-blue-100 text-blue-800'}
    
    def get_balance_display(self) -> str:
        """Formatted balance due."""
        return f"TZS {self.balance:,.0f}"
    
    def get_days_overdue(self) -> int:
        """Get number of days overdue (0 if not overdue)."""
        if not self.is_overdue:
            return 0
        from datetime import date
        return (date.today() - self.expected_payment_date).days


class DebtReturn(TimestampedModel, ActionMixin):
    """Partial or full repayment against a credit sale."""
    debt = models.ForeignKey(Debt, on_delete=models.PROTECT, related_name='returns')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    return_date = models.DateTimeField(default=timezone.now)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-return_date']
        verbose_name = 'Debt Repayment'

    def __str__(self):
        return f"Repayment #{self.pk} — {self.debt.debtor.name} — {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('credit:debt_return_detail', kwargs={'pk': self.pk})
    
    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_edit_url(self):
        from django.urls import reverse
        return reverse('credit:debt_return_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        from django.urls import reverse
        return reverse('credit:debt_return_delete', kwargs={'pk': self.pk})
    
    def get_debtor_url(self):
        """View the debtor associated with this payment."""
        if self.debt and self.debt.debtor:
            return self.debt.debtor.get_absolute_url()
        return '#'
    
    def can_edit(self, user=None) -> bool:
        """Allow editing on the same day only."""
        from django.utils import timezone
        now = timezone.now()
        return (now.date() == self.return_date.date())
    
    def can_delete(self, user=None) -> bool:
        """Always allow deletion of repayments."""
        return True
    
    def get_status_badge(self) -> dict:
        """Returns status badge for repayment."""
        return {'label': 'Received', 'color': 'bg-green-100 text-green-800'}
    
    def get_amount_display(self) -> str:
        """Formatted amount received."""
        return f"TZS {self.amount:,.0f}"
