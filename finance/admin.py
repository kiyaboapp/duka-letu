from django.contrib import admin
from .models import (
    PaymentMethod, ExpenseType, ExpenseItem, ExpenseRate,
    RecurrencePattern, PaymentObligation, Payment, Prepayment,
    PaymentAllocation, LiabilityCategory, LiabilityType,
    LiabilityItem, LiabilityPaymentDetail
)


class ExpenseRateInline(admin.TabularInline):
    model = ExpenseRate
    extra = 1
    ordering = ['-effective_from']


class RecurrencePatternInline(admin.StackedInline):
    model = RecurrencePattern
    extra = 0


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'expense_type', 'current_rate_display', 'is_active']
    list_filter = ['expense_type', 'is_active']
    inlines = [ExpenseRateInline, RecurrencePatternInline]

    def current_rate_display(self, obj):
        rate = obj.current_rate()
        return f"TZS {rate:,.0f}"
    current_rate_display.short_description = 'Current Rate'


@admin.register(PaymentObligation)
class PaymentObligationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'due_date', 'amount_due', 'balance', 'payment_status']
    list_filter = ['obligation_type', 'due_date']
    date_hierarchy = 'due_date'

    def get_name(self, obj):
        if obj.expense_item:
            return obj.expense_item.name
        if obj.liability_item:
            return obj.liability_item.name
        return '—'
    get_name.short_description = 'Item'


admin.site.register(PaymentMethod)
admin.site.register(ExpenseType)
admin.site.register(ExpenseRate)
admin.site.register(RecurrencePattern)
admin.site.register(Payment)
admin.site.register(Prepayment)
admin.site.register(PaymentAllocation)
admin.site.register(LiabilityCategory)
admin.site.register(LiabilityType)
admin.site.register(LiabilityItem)
admin.site.register(LiabilityPaymentDetail)

# Register your models here.
