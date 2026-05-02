from django import forms
from django.core.exceptions import ValidationError
from .models import Sale, ReturnInward, SaleOfficeUse, Drawing, OfficeUseCategory, DrawingCategory
from catalog.models import ProductSpec

TW = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
TW_TEXTAREA = TW + ' resize-none'
TW_NUM = 'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none'


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product_spec', 'quantity', 'unit_price', 'discount', 'sale_date', 'payment_method', 'notes']
        widgets = {
            'product_spec': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'class': TW_NUM, 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': TW_NUM, 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': TW_NUM, 'step': '0.01'}),
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}),
            'payment_method': forms.Select(attrs={'class': TW}),
            'notes': forms.Textarea(attrs={'class': TW + ' resize-none', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product_spec = cleaned_data.get('product_spec')
        quantity = cleaned_data.get('quantity')

        if product_spec and quantity:
            if product_spec.current_stock < quantity:
                raise ValidationError(
                    f'Insufficient stock. Available: {product_spec.current_stock}, Required: {quantity}'
                )
        return cleaned_data


class ReturnInwardForm(forms.ModelForm):
    class Meta:
        model = ReturnInward
        fields = ['sale', 'quantity', 'unit_price', 'reason', 'sale_date']
        widgets = {
            'sale': forms.Select(attrs={'class': TW}),
            'quantity': forms.NumberInput(attrs={'class': TW}),
            'unit_price': forms.NumberInput(attrs={'class': TW}),
            'reason': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 3}),
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}),
        }


class SaleOfficeUseForm(forms.ModelForm):
    class Meta:
        model = SaleOfficeUse
        fields = ['product_spec', 'original_sale', 'office_use_category', 'quantity',
                  'unit_price', 'discount', 'sale_date', 'reason']
        widgets = {
            'product_spec': forms.Select(attrs={'class': TW}),
            'original_sale': forms.Select(attrs={'class': TW}),
            'office_use_category': forms.Select(attrs={'class': TW}),
            'quantity': forms.NumberInput(attrs={'class': TW}),
            'unit_price': forms.NumberInput(attrs={'class': TW}),
            'discount': forms.NumberInput(attrs={'class': TW}),
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}),
            'reason': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product_spec = cleaned_data.get('product_spec')
        quantity = cleaned_data.get('quantity')

        if product_spec and quantity:
            if product_spec.current_stock < quantity:
                raise ValidationError(
                    f'Insufficient stock. Available: {product_spec.current_stock}, Required: {quantity}'
                )
        return cleaned_data


class DrawingForm(forms.ModelForm):
    class Meta:
        model = Drawing
        fields = ['drawing_category', 'product_spec', 'quantity', 'unit_price', 'discount', 'sale_date', 'notes']
        widgets = {
            'drawing_category': forms.Select(attrs={'class': TW}),
            'product_spec': forms.Select(attrs={'class': TW}),
            'quantity': forms.NumberInput(attrs={'class': TW}),
            'unit_price': forms.NumberInput(attrs={'class': TW}),
            'discount': forms.NumberInput(attrs={'class': TW}),
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}),
            'notes': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product_spec = cleaned_data.get('product_spec')
        quantity = cleaned_data.get('quantity')

        if product_spec and quantity:
            if product_spec.current_stock < quantity:
                raise ValidationError(
                    f'Insufficient stock. Available: {product_spec.current_stock}, Required: {quantity}'
                )
        return cleaned_data
