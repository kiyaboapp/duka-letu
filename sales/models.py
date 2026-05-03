from django.db import models
from django.utils import timezone
from catalog.models import ProductSpec
from finance.models import PaymentMethod


class Sale(models.Model):
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
        super().save(*args, **kwargs)
        if not self.reference_number:
            self.reference_number = f"SL-{self.sale_date.year}-{self.pk:06d}"
            Sale.objects.filter(pk=self.pk).update(reference_number=self.reference_number)
        self.product_spec.update_stock()


class ReturnInward(models.Model):
    """Sales return — customer returns goods."""
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='returns')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField(blank=True)
    sale_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-sale_date']

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sale.product_spec.update_stock()


class OfficeUseCategory(models.Model):
    """e.g., 'Customer Care', 'Display', 'Staff Use'"""
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Office Use Categories'

    def __str__(self):
        return self.name


class SaleOfficeUse(models.Model):
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

    @property
    def amount(self):
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()


class DrawingCategory(models.Model):
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Drawing Categories'

    def __str__(self):
        return self.name


class Drawing(models.Model):
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

# Create your models here.
