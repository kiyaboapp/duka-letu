from django.contrib import admin
from .models import AssetCategory, AssetType, Asset


admin.site.register(AssetCategory)
admin.site.register(AssetType)
admin.site.register(Asset)

# Register your models here.
