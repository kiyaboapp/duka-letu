from django.db import models
from django.utils import timezone
from django.db.models import Sum, ExpressionWrapper, DecimalField, F
from django.db.models.functions import Coalesce
from decimal import Decimal
from catalog.models import ProductSpec
from finance.models import PaymentMethod
from apps.core.models import TimestampedModel


class Debtor(TimestampedModel):
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


class Debt(TimestampedModel):
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
        self.product_spec.update_stock()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('credit:debt_detail', kwargs={'pk': self.pk})


class DebtReturn(TimestampedModel):
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
        # Trigger stock update if needed (though repayments don't affect stock directly)
        # Keeping for consistency with other transaction models
        self.debt.product_spec.update_stock()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('credit:debt_return_detail', kwargs={'pk': self.pk})
