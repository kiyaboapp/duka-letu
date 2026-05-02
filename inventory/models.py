from django.db import models
from django.utils import timezone
from catalog.models import ProductSpec


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases')
    purchase_date = models.DateTimeField(default=timezone.now)
    invoice_number = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-purchase_date']

    def __str__(self):
        return f"Purchase #{self.pk} — {self.supplier.name} ({self.purchase_date.date()})"

    @property
    def total_amount(self):
        return sum(d.amount for d in self.details.all())

    @property
    def period_label(self):
        return self.purchase_date.strftime('%B %Y')


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='details')
    product_spec = models.ForeignKey(ProductSpec, on_delete=models.PROTECT, related_name='purchase_details')
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    suggested_selling_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['product_spec__product__name']

    def __str__(self):
        return f"{self.product_spec} × {self.quantity} @ {self.unit_cost}"

    @property
    def amount(self):
        return self.quantity * self.unit_cost

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_spec.update_stock()


class ReturnOutward(models.Model):
    """Purchase return — goods sent back to supplier."""
    purchase_detail = models.ForeignKey(PurchaseDetail, on_delete=models.PROTECT, related_name='returns')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField(blank=True)
    sale_date = models.DateTimeField(default=timezone.now)  # kept as 'sale_date' for migration compat

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"Return Outward #{self.pk}"

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.purchase_detail.product_spec.update_stock()

# Create your models here.
