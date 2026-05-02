from django.db import models
from django.utils import timezone


class AssetCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.name


class AssetType(models.Model):
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='types')
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class Asset(models.Model):
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, related_name='assets')
    name = models.CharField(max_length=255)
    worth = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True)
    date_checked = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['asset_type__name', 'name']

    def __str__(self):
        return self.name

# Create your models here.
