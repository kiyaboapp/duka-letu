from django.contrib import admin
from .models import Supplier, Purchase, PurchaseDetail, ReturnOutward


class PurchaseDetailInline(admin.TabularInline):
    model = PurchaseDetail
    extra = 1
    fields = ['product_spec', 'quantity', 'unit_cost', 'suggested_selling_price']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'purchase_date', 'invoice_number', 'total_amount', 'item_count']
    list_filter = ['supplier', 'purchase_date']
    search_fields = ['supplier__name', 'invoice_number']
    inlines = [PurchaseDetailInline]
    date_hierarchy = 'purchase_date'

    def total_amount(self, obj):
        return f"TZS {obj.total_amount:,.0f}"

    def item_count(self, obj):
        return obj.details.count()
    item_count.short_description = 'Items'


admin.site.register(Supplier)
admin.site.register(PurchaseDetail)
admin.site.register(ReturnOutward)

# Register your models here.
