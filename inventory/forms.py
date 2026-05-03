from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import Supplier, Purchase, PurchaseDetail, ReturnOutward
from catalog.models import ProductSpec

TW = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
TW_TEXTAREA = TW + ' resize-none'
NOW_STR = lambda: timezone.now().strftime('%Y-%m-%dT%H:%M')


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'purchase_date', 'invoice_number', 'carriage_inwards', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': TW}),
            'purchase_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}, format='%Y-%m-%dT%H:%M'),
            'invoice_number': forms.TextInput(attrs={'class': TW}),
            'carriage_inwards': forms.NumberInput(attrs={'class': TW, 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial.setdefault('purchase_date', NOW_STR())


class PurchaseDetailForm(forms.ModelForm):
    class Meta:
        model = PurchaseDetail
        fields = ['product_spec', 'quantity', 'unit_cost', 'suggested_selling_price']
        widgets = {
            'product_spec': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'class': TW}),
            'unit_cost': forms.NumberInput(attrs={'class': TW}),
            'suggested_selling_price': forms.NumberInput(attrs={'class': TW}),
        }


PurchaseDetailFormSet = inlineformset_factory(
    Purchase, PurchaseDetail,
    form=PurchaseDetailForm,
    extra=1,
    can_delete=True,
)


class ReturnOutwardForm(forms.ModelForm):
    class Meta:
        model = ReturnOutward
        fields = ['purchase_detail', 'quantity', 'unit_price', 'reason', 'sale_date']
        widgets = {
            'purchase_detail': forms.Select(attrs={'class': TW}),
            'quantity': forms.NumberInput(attrs={'class': TW}),
            'unit_price': forms.NumberInput(attrs={'class': TW}),
            'reason': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 1}),
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial.setdefault('sale_date', NOW_STR())
