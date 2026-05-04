from django.db import models
from django.utils import timezone
from decimal import Decimal
from apps.core.models import TimestampedModel


class AssetCategory(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assets:asset_category_detail', kwargs={'pk': self.pk})


class AssetType(TimestampedModel):
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assets:asset_type_detail', kwargs={'pk': self.pk})


class Asset(TimestampedModel):
    DEPRECIATION_METHODS = [
        ('SL', 'Straight-Line'),
        ('DB', 'Declining Balance'),
        ('NONE', 'No Depreciation'),
    ]

    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, related_name='assets')
    name = models.CharField(max_length=255)
    asset_reference = models.CharField(max_length=50, blank=True, db_index=True)
    # worth kept for backward compat with existing data
    worth = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     help_text='Original purchase price (TZS).')
    acquisition_date = models.DateField(default=timezone.now)
    depreciation_method = models.CharField(max_length=10, choices=DEPRECIATION_METHODS, default='SL')
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.20'),
                                            help_text='Annual rate e.g. 0.20 = 20% p.a.')
    residual_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    disposal_date = models.DateField(null=True, blank=True)
    disposal_proceeds = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    date_checked = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['asset_type__name', 'name']

    def __str__(self):
        return f"{self.asset_reference or self.name} — {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.asset_reference:
            Asset.objects.filter(pk=self.pk).update(asset_reference=f"FA-{self.pk:03d}")
            self.asset_reference = f"FA-{self.pk:03d}"
        # Keep worth in sync with cost_price for backward compat
        if self.cost_price and not self.worth:
            Asset.objects.filter(pk=self.pk).update(worth=self.cost_price)

    @property
    def effective_cost(self):
        """Use cost_price if set, fall back to worth for legacy records."""
        return self.cost_price if self.cost_price else self.worth

    @property
    def accumulated_depreciation(self) -> Decimal:
        return self.get_accumulated_depreciation(timezone.now().date())

    def get_accumulated_depreciation(self, as_of_date) -> Decimal:
        if self.depreciation_method == 'NONE' or not self.effective_cost:
            return Decimal('0')
        
        # Acquisition date must be on or before as_of_date
        if self.acquisition_date > as_of_date:
            return Decimal('0')

        # End date for depreciation is either disposal_date or as_of_date, whichever is earlier
        end_date = as_of_date
        if self.disposal_date and self.disposal_date < end_date:
            end_date = self.disposal_date
            
        years = Decimal((end_date - self.acquisition_date).days) / Decimal('365.25')
        if years < 0:
            return Decimal('0')

        depreciable = self.effective_cost - self.residual_value
        if self.depreciation_method == 'SL':
            acc = depreciable * self.depreciation_rate * years
        else:  # DB
            acc = self.effective_cost * (1 - (1 - self.depreciation_rate) ** float(years))
            acc = Decimal(str(acc))
        return min(acc, depreciable).quantize(Decimal('0.01'))

    @property
    def net_book_value(self) -> Decimal:
        return self.effective_cost - self.accumulated_depreciation

    @property
    def annual_depreciation_charge(self) -> Decimal:
        if self.depreciation_method == 'NONE':
            return Decimal('0')
        return ((self.effective_cost - self.residual_value) * self.depreciation_rate).quantize(Decimal('0.01'))

    @property
    def monthly_depreciation_charge(self) -> Decimal:
        return (self.annual_depreciation_charge / 12).quantize(Decimal('0.01'))

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assets:asset_detail', kwargs={'pk': self.pk})
