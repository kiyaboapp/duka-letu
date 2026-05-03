from django.db import models
from django.utils import timezone
from decimal import Decimal
from catalog.models import ProductSpec
from finance.models import PaymentMethod
from apps.core.models import TimestampedModel
from apps.core.services import ActionMixin


class Sale(TimestampedModel, ActionMixin):
    """Direct cash sale at the counter."""
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='sales')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True, blank=True)
    notes = models.TextField(blank=True)
    reference_number = models.CharField(max_length=50, blank=True, db_index=True)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"Sale #{self.pk} — {self.product_spec} ({self.sale_date.date()})"

    @property
    def amount(self):
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.reference_number:
            self.reference_number = f"SL-{self.sale_date.year}-{self.pk:06d}"
            Sale.objects.filter(pk=self.pk).update(reference_number=self.reference_number)
        self.product_spec.update_stock()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sales:sale_detail', kwargs={'pk': self.pk})

    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_edit_url(self):
        from django.urls import reverse
        return reverse('sales:sale_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        from django.urls import reverse
        return reverse('sales:sale_delete', kwargs={'pk': self.pk})
    
    def get_return_url(self):
        """URL to create a return for this sale."""
        from django.urls import reverse
        return f"{reverse('sales:return_inward_create')}?sale={self.pk}"
    
    def get_duplicate_url(self):
        """URL to duplicate this sale."""
        from django.urls import reverse
        return f"{reverse('sales:sale_create')}?product_spec={self.product_spec_id}&quantity={self.quantity}&unit_price={self.unit_price}"
    
    def can_return(self):
        """Check if this sale can be returned (has remaining quantity)."""
        returned_qty = sum(r.quantity for r in self.returns.all())
        return self.quantity > returned_qty
    
    def get_remaining_quantity(self):
        """Get quantity available for return."""
        returned_qty = sum(r.quantity for r in self.returns.all())
        return max(0, self.quantity - returned_qty)
    
    # Override ActionMixin for business-specific rules
    def can_edit(self, user=None) -> bool:
        """Allow editing only on the same day (simplified rule)."""
        from django.utils import timezone
        now = timezone.now()
        return (now.date() == self.sale_date.date())
    
    def can_delete(self, user=None) -> bool:
        """Prevent deletion if returns exist."""
        return not self.returns.exists()
    
    def can_duplicate(self) -> bool:
        """Always allow duplicating sales."""
        return True
    
    def get_status_badge(self) -> dict:
        """Returns status badge based on return status."""
        if self.get_remaining_quantity() < self.quantity:
            return {'label': 'Partially Returned', 'color': 'bg-yellow-100 text-yellow-800'}
        elif not self.can_return():
            return {'label': 'Fully Returned', 'color': 'bg-gray-100 text-gray-800'}
        else:
            return {'label': 'Completed', 'color': 'bg-green-100 text-green-800'}
    
    def get_profit_amount(self) -> Decimal:
        """Calculate profit for this sale line."""
        return self.amount - (self.quantity * self.product_spec.cached_wac)
    
    def get_profit_margin_percent(self) -> float:
        """Calculate profit margin percentage."""
        cost = self.quantity * self.product_spec.cached_wac
        if cost > 0:
            profit = self.amount - cost
            return round((profit / cost) * 100, 2)
        return 0.0


class ReturnInward(TimestampedModel):
    """Sales return — customer returns goods."""
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='returns')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField(blank=True)
    sale_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"Return Inward #{self.pk} — {self.sale.product_spec}"

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sale.product_spec.update_stock()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sales:return_inward_detail', kwargs={'pk': self.pk})


class OfficeUseCategory(TimestampedModel):
    """e.g., 'Customer Care', 'Display', 'Staff Use'"""
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Office Use Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sales:office_use_category_detail', kwargs={'pk': self.pk})


class SaleOfficeUse(TimestampedModel):
    """Internal product consumption — office use / customer care."""
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='office_uses')
    original_sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='office_use_conversions')
    office_use_category = models.ForeignKey(OfficeUseCategory, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Sale — Office Use'
        verbose_name_plural = 'Sales — Office Use'

    def __str__(self):
        return f"Office Use #{self.pk} — {self.product_spec}"

    @property
    def amount(self):
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sales:office_use_detail', kwargs={'pk': self.pk})


class DrawingCategory(TimestampedModel):
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Drawing Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sales:drawing_category_detail', kwargs={'pk': self.pk})


class Drawing(TimestampedModel):
    """Owner withdrawals — goods or cash taken for personal use."""
    DRAWING_TYPES = [('GOODS', 'Goods'), ('CASH', 'Cash')]
    drawing_category = models.ForeignKey(DrawingCategory, on_delete=models.PROTECT)
    drawing_type = models.CharField(max_length=10, choices=DRAWING_TYPES, default='GOODS')
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='drawings',
                                     null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                      help_text='TZS amount for cash drawings.')
    sale_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"Drawing #{self.pk} — {self.drawing_type} ({self.sale_date.date()})"

    @property
    def amount(self):
        if self.drawing_type == 'CASH':
            return self.cash_amount
        if self.product_spec:
            return (self.quantity * self.unit_price) - self.discount
        return Decimal('0')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.product_spec:
            self.product_spec.update_stock()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sales:drawing_detail', kwargs={'pk': self.pk})
    
    # Self-sufficient methods for Drawing model
    def can_edit(self, user=None) -> bool:
        """Allow editing only on the same day."""
        from django.utils import timezone
        now = timezone.now()
        return (now.date() == self.sale_date.date())
    
    def can_delete(self, user=None) -> bool:
        """Always allow deletion of drawings (no dependent records)."""
        return True
    
    def get_status_badge(self) -> dict:
        """Returns status badge based on drawing type."""
        if self.drawing_type == 'CASH':
            return {'label': 'Cash Drawing', 'color': 'bg-blue-100 text-blue-800'}
        else:
            return {'label': 'Goods Drawing', 'color': 'bg-purple-100 text-purple-800'}
