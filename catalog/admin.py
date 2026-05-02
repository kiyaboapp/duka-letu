from django.contrib import admin
from .models import Category, ProductType, Brand, Unit, Spec, SpecValue, Product, ProductSpec


class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_count']
    search_fields = ['name']
    inlines = [ProductTypeInline]

    def type_count(self, obj):
        return obj.types.count()
    type_count.short_description = 'Types'


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 0
    fields = ['spec_value', 'default_cost_price', 'default_selling_price',
              'reorder_level', 'current_stock']
    readonly_fields = ['current_stock']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'brand', 'unit', 'spec_count', 'total_stock']
    list_filter = ['product_type__category', 'brand']
    search_fields = ['name', 'brand__name']
    inlines = [ProductSpecInline]

    def spec_count(self, obj):
        return obj.specs.count()

    def total_stock(self, obj):
        return sum(s.current_stock for s in obj.specs.all())
    total_stock.short_description = 'Stock'


@admin.register(ProductSpec)
class ProductSpecAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'current_stock', 'is_low_stock', 'default_selling_price']
    list_filter = ['product__product_type__category', 'product__brand']
    search_fields = ['product__name', 'spec_value__value']
    readonly_fields = ['current_stock']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low?'


admin.site.register(Brand)
admin.site.register(Unit)
admin.site.register(Spec)
admin.site.register(SpecValue)
admin.site.register(ProductType)

# Register your models here.
