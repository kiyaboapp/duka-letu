from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductType(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = [['category', 'name']]
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.abbreviation or self.name


class Spec(models.Model):
    """Spec dimension — e.g., 'Size', 'Color', 'Material'"""
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SpecValue(models.Model):
    """Concrete spec value — e.g., 'A4', 'Blue', 'Plastic'"""
    spec = models.ForeignKey(Spec, on_delete=models.PROTECT, related_name='values')
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = [['spec', 'value']]
        ordering = ['spec__name', 'value']

    def __str__(self):
        return f"{self.spec.name}: {self.value}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image_path = models.CharField(max_length=255, blank=True)  # legacy 'path' field

    class Meta:
        unique_together = [['name', 'product_type', 'brand']]
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def category(self):
        return self.product_type.category


class ProductSpec(models.Model):
    """
    A specific variant of a product — the sellable/purchasable unit.
    e.g., "A4 Notebook" (product) + "Blue" (spec_value) = one ProductSpec.
    Every transaction references a ProductSpec, not a Product.
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='specs')
    spec_value = models.ForeignKey(SpecValue, on_delete=models.PROTECT, related_name='product_specs')
    default_cost_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    default_selling_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reorder_level = models.PositiveIntegerField(default=5)
    current_stock = models.IntegerField(default=0)

    class Meta:
        unique_together = [['product', 'spec_value']]
        ordering = ['product__name', 'spec_value__value']

    def __str__(self):
        return f"{self.product.name} ({self.spec_value.value})"

    def update_stock(self):
        """
        Recalculate current_stock from all transaction tables.
        Call after any transaction that affects this product spec.
        Mirrors modStockCRUD.UpdateProductsStock().
        """
        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        def _sum(qs):
            return qs.aggregate(t=Coalesce(Sum('quantity'), 0))['t']

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

    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.current_stock <= 0

# Create your models here.
