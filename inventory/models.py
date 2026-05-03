from django.db import models
from django.utils import timezone
from catalog.models import ProductSpec
from apps.core.models import TimestampedModel
from apps.core.services import ActionMixin


class Supplier(TimestampedModel, ActionMixin):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('inventory:supplier_detail', kwargs={'pk': self.pk})

    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_edit_url(self):
        from django.urls import reverse
        return reverse('inventory:supplier_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        from django.urls import reverse
        return reverse('inventory:supplier_delete', kwargs={'pk': self.pk})
    
    def get_purchase_url(self):
        """Create a new purchase order for this supplier."""
        from django.urls import reverse
        return f"{reverse('inventory:purchase_create')}?supplier={self.pk}"
    
    def get_contacts_url(self):
        """View contact details modal."""
        return self.get_absolute_url()
    
    # Override ActionMixin methods for Supplier-specific logic
    def can_delete(self, user=None) -> bool:
        """Prevent deletion if supplier has purchases."""
        return not self.purchases.exists()
    
    def get_status_badge(self) -> dict:
        """Returns status badge based on activity."""
        purchase_count = self.purchases.count()
        if purchase_count > 10:
            return {'label': 'Active Supplier', 'color': 'bg-green-100 text-green-800'}
        elif purchase_count > 0:
            return {'label': 'Occasional Supplier', 'color': 'bg-yellow-100 text-yellow-800'}
        else:
            return {'label': 'New Supplier', 'color': 'bg-gray-100 text-gray-800'}
    
    def get_total_purchased_amount(self) -> float:
        """Calculate total amount purchased from this supplier."""
        total = sum(p.total_amount for p in self.purchases.all())
        return float(total)
    
    def get_last_purchase_date(self):
        """Get date of last purchase."""
        last = self.purchases.order_by('-purchase_date').first()
        return last.purchase_date if last else None


class Purchase(TimestampedModel, ActionMixin):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases')
    purchase_date = models.DateTimeField(default=timezone.now)
    invoice_number = models.CharField(max_length=255, blank=True)
    carriage_inwards = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                           help_text='Transport/freight cost to bring goods to shop.')
    notes = models.TextField(blank=True)

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

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('inventory:purchase_detail', kwargs={'pk': self.pk})

    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_edit_url(self):
        from django.urls import reverse
        return reverse('inventory:purchase_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        from django.urls import reverse
        return reverse('inventory:purchase_delete', kwargs={'pk': self.pk})
    
    def get_add_items_url(self):
        """Add more items to this purchase."""
        from django.urls import reverse
        return f"{reverse('inventory:purchase_detail', kwargs={'pk': self.pk})}#add-items"
    
    def get_return_items_url(self):
        """Return items to supplier."""
        from django.urls import reverse
        return f"{reverse('inventory:return_outward_create')}?purchase={self.pk}"
    
    def get_duplicate_url(self):
        """Create similar purchase from same supplier."""
        from django.urls import reverse
        return f"{reverse('inventory:purchase_create')}?supplier={self.supplier_id}"
    
    def can_add_items(self):
        """Check if we can still add items (purchase not finalized)."""
        # In future: add 'is_finalized' field to Purchase model
        return True
    
    def can_return_items(self):
        """Check if items can be returned."""
        return self.details.exists()
    
    # Override ActionMixin methods for Purchase-specific logic
    def can_edit(self, user=None) -> bool:
        """Allow editing only on the same day (simplified)."""
        from django.utils import timezone
        now = timezone.now()
        return (now.date() == self.purchase_date.date())
    
    def can_delete(self, user=None) -> bool:
        """Prevent deletion if there are return outwards."""
        from inventory.models import ReturnOutward
        return not ReturnOutward.objects.filter(purchase_detail__purchase=self).exists()
    
    def can_duplicate(self) -> bool:
        """Always allow duplicating purchases."""
        return True
    
    def get_status_badge(self) -> dict:
        """Returns status badge based on purchase state."""
        if self.carriage_inwards > 0:
            return {'label': 'Complete', 'color': 'bg-green-100 text-green-800'}
        else:
            return {'label': 'Pending Freight', 'color': 'bg-yellow-100 text-yellow-800'}
    
    def get_item_count(self) -> int:
        """Get number of line items in this purchase."""
        return self.details.count()
    
    def get_total_cost_with_freight(self) -> float:
        """Calculate total amount including carriage inwards."""
        return float(self.total_amount + self.carriage_inwards)


class PurchaseDetail(TimestampedModel):
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

    def delete(self, *args, **kwargs):
        spec = self.product_spec
        super().delete(*args, **kwargs)
        spec.update_stock()


class ReturnOutward(TimestampedModel):
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

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('inventory:return_outward_detail', kwargs={'pk': self.pk})

    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_edit_url(self):
        from django.urls import reverse
        return reverse('inventory:return_outward_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        from django.urls import reverse
        return reverse('inventory:return_outward_delete', kwargs={'pk': self.pk})
    
    def get_purchase_url(self):
        """View the original purchase."""
        if self.purchase_detail and self.purchase_detail.purchase:
            from django.urls import reverse
            return reverse('inventory:purchase_detail', kwargs={'pk': self.purchase_detail.purchase.pk})
        return '#'
