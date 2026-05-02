from django.contrib import admin
from .models import Debtor, Debt, DebtReturn


class DebtInline(admin.TabularInline):
    model = Debt
    extra = 0
    fields = ['product_spec', 'quantity', 'unit_price', 'sale_date', 'expected_payment_date']
    readonly_fields = ['sale_date']


class DebtReturnInline(admin.TabularInline):
    model = DebtReturn
    extra = 1
    fields = ['amount', 'payment_method', 'return_date', 'comment']


@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_1', 'outstanding_balance', 'nida_id']
    search_fields = ['name', 'phone_1', 'nida_id']
    inlines = [DebtInline]

    def outstanding_balance(self, obj):
        bal = obj.outstanding_balance
        return f"TZS {bal:,.0f}"
    outstanding_balance.short_description = 'Outstanding'


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['id', 'debtor', 'product_spec', 'amount_due', 'balance', 'expected_payment_date', 'is_overdue']
    list_filter = ['debtor', 'expected_payment_date']
    inlines = [DebtReturnInline]

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True


admin.site.register(DebtReturn)

# Register your models here.
