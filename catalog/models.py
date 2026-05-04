from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from apps.core.models import TimestampedModel
from apps.core.services import ActionMixin

_DEC = DecimalField(max_digits=15, decimal_places=2)


class Category(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductType(TimestampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = [['category', 'name']]
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class Brand(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.abbreviation or self.name


class Spec(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SpecValue(TimestampedModel):
    spec = models.ForeignKey(Spec, on_delete=models.PROTECT, related_name='values')
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = [['spec', 'value']]
        ordering = ['spec__name', 'value']

    def __str__(self):
        return f"{self.spec.name}: {self.value}"


class Product(TimestampedModel):
    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image_path = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = [['name', 'product_type', 'brand']]
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def category(self):
        return self.product_type.category

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catalog:product_detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        from django.urls import reverse
        return reverse('catalog:product_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        from django.urls import reverse
        return reverse('catalog:product_delete', kwargs={'pk': self.pk})


class ProductSpec(TimestampedModel, ActionMixin):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='specs')
    spec_value = models.ForeignKey(SpecValue, on_delete=models.PROTECT, related_name='product_specs')
    default_cost_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    default_selling_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reorder_level = models.PositiveIntegerField(default=5)
    current_stock = models.IntegerField(default=0)
    cached_wac = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name='Cached Weighted Avg Cost')
    cached_stock_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                             verbose_name='Cached Stock Value (TZS)')
    budget_monthly_sales_qty = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [['product', 'spec_value']]
        ordering = ['product__name', 'spec_value__value']

    def __str__(self):
        return f"{self.product.name} ({self.spec_value.value})"
    
    # Override ActionMixin defaults for specific business rules
    def can_edit(self, user=None) -> bool:
        """Allow editing unless there are transactions (simplified - in production check transaction history)."""
        return True
    
    def can_delete(self, user=None) -> bool:
        """Prevent deletion if there's any stock or transaction history."""
        return self.current_stock == 0 and not self.cached_wac > 0
    
    def get_status_badge(self) -> dict:
        """Returns status info for UI badges with Tailwind classes."""
        if self.is_out_of_stock():
            return {'label': 'Out of Stock', 'color': 'bg-red-100 text-red-800'}
        elif self.needs_reorder():
            return {'label': 'Low Stock', 'color': 'bg-yellow-100 text-yellow-800'}
        else:
            return {'label': 'In Stock', 'color': 'bg-green-100 text-green-800'}

    def update_stock(self):
        from django.db.models.functions import Coalesce as C

        def _sum(qs):
            return qs.aggregate(t=C(Sum('quantity'), 0))['t']

        from inventory.models import PurchaseDetail, ReturnOutward
        from sales.models import Sale, ReturnInward, SaleOfficeUse, Drawing
        from credit.models import Debt

        purchased = _sum(PurchaseDetail.objects.filter(product_spec=self))
        ret_in = _sum(ReturnInward.objects.filter(sale__product_spec=self))
        sold = _sum(Sale.objects.filter(product_spec=self))
        credit = _sum(Debt.objects.filter(product_spec=self))
        ret_out = _sum(ReturnOutward.objects.filter(purchase_detail__product_spec=self))
        office = _sum(SaleOfficeUse.objects.filter(product_spec=self))
        drawings = _sum(Drawing.objects.filter(product_spec=self))

        self.current_stock = purchased + ret_in - sold - credit - ret_out - office - drawings
        self.save(update_fields=['current_stock'])
        self.refresh_wac()

    def refresh_wac(self):
        """Recalculate cached WAC using ExpressionWrapper — amount is a @property."""
        from inventory.models import PurchaseDetail
        cost_expr = ExpressionWrapper(F('quantity') * F('unit_cost'), output_field=_DEC)
        agg = PurchaseDetail.objects.filter(product_spec=self).aggregate(
            total_cost=Coalesce(Sum(cost_expr), Decimal('0'), output_field=_DEC),
            total_qty=Coalesce(Sum('quantity'), 0),
        )
        if agg['total_qty'] > 0:
            self.cached_wac = agg['total_cost'] / agg['total_qty']
        else:
            self.cached_wac = Decimal('0')
        self.cached_stock_value = Decimal(self.current_stock) * self.cached_wac
        self.save(update_fields=['cached_wac', 'cached_stock_value'])

    @property
    def is_low_stock(self):
        return 0 < self.current_stock <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.current_stock <= 0

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catalog:product_detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        from django.urls import reverse
        return reverse('catalog:product_detail', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return '#'

    # ── SELF-SUFFICIENT ACTIONS ────────────────────────────────────────
    
    def get_sell_url(self):
        """Direct URL to sell this product."""
        from django.urls import reverse
        return f"{reverse('sales:sale_create')}?product_spec={self.pk}"
    
    def get_purchase_url(self):
        """Direct URL to purchase more of this product."""
        from django.urls import reverse
        return f"{reverse('inventory:purchase_create')}?product_spec={self.pk}"
    
    def get_credit_sale_url(self):
        """Direct URL to create credit sale for this product."""
        from django.urls import reverse
        return f"{reverse('credit:debt_create')}?product_spec={self.pk}"
    
    def get_adjust_stock_url(self):
        """URL to stock adjustment form (if implemented)."""
        from django.urls import reverse
        try:
            return reverse('catalog:product_spec_adjust_stock', kwargs={'pk': self.pk})
        except:
            return '#'
    
    def get_history_url(self):
        """URL to transaction history for this product."""
        from django.urls import reverse
        return reverse('catalog:product_detail', kwargs={'pk': self.pk})
    
    def can_sell(self):
        """Check if product can be sold (has stock)."""
        return self.current_stock > 0
    
    def can_purchase(self):
        """Always allow purchases."""
        return True
    
    def needs_reorder(self):
        """Check if product needs reordering."""
        return self.current_stock <= self.reorder_level and self.current_stock > 0
    
    def is_out_of_stock(self):
        """Check if product is out of stock."""
        return self.current_stock <= 0
    
    def get_status_badge_class(self):
        """Return Tailwind CSS classes for status badge."""
        if self.is_out_of_stock():
            return 'bg-red-100 text-red-800'
        elif self.needs_reorder():
            return 'bg-yellow-100 text-yellow-800'
        else:
            return 'bg-green-100 text-green-800'
    
    def get_status_label(self):
        """Return human-readable status label."""
        if self.is_out_of_stock():
            return 'Out of Stock'
        elif self.needs_reorder():
            return 'Low Stock'
        else:
            return 'In Stock'
    
    # Additional self-sufficient methods for template convenience
    def get_profit_margin_percent(self) -> float:
        cost = self.cached_wac or self.default_cost_price or Decimal('0')
        price = self.default_selling_price or Decimal('0')
        if cost > 0 and price > 0:
            return round(float((price - cost) / cost * 100), 2)
        return 0.0
    
    def get_reorder_quantity_suggestion(self) -> int:
        """Suggest reorder quantity based on budget monthly sales."""
        if self.budget_monthly_sales_qty > 0:
            # Suggest ordering enough for 2 months minus current stock
            suggested = (self.budget_monthly_sales_qty * 2) - self.current_stock
            return max(0, suggested)
        return 0
    
    def get_quick_actions(self) -> list:
        """Returns list of quick action URLs available for this product."""
        actions = []
        if self.can_sell():
            actions.append({'label': 'Sell', 'url': self.get_sell_url(), 'icon': '💰'})
        if self.can_purchase():
            actions.append({'label': 'Purchase', 'url': self.get_purchase_url(), 'icon': '📦'})
        actions.append({'label': 'Credit Sale', 'url': self.get_credit_sale_url(), 'icon': '📒'})
        return actions
