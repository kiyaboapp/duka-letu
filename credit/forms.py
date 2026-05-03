from django import forms
from django.core.exceptions import ValidationError
from .models import Debtor, Debt, DebtReturn
from catalog.models import ProductSpec

TW = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
TW_TEXTAREA = TW + ' resize-none'


class DebtorForm(forms.ModelForm):
    class Meta:
        model = Debtor
        fields = ['name', 'address', 'phone_1', 'phone_2', 'nida_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': TW}),
            'address': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 1}),
            'phone_1': forms.TextInput(attrs={'class': TW}),
            'phone_2': forms.TextInput(attrs={'class': TW}),
            'nida_id': forms.TextInput(attrs={'class': TW}),
        }


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['debtor', 'product_spec', 'quantity', 'unit_price', 'discount',
                  'sale_date', 'expected_payment_date']
        widgets = {
            'debtor': forms.Select(attrs={'class': TW}),
            'product_spec': forms.Select(attrs={'class': TW}),
            'quantity': forms.NumberInput(attrs={'class': TW}),
            'unit_price': forms.NumberInput(attrs={'class': TW}),
            'discount': forms.NumberInput(attrs={'class': TW}),
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}, format='%Y-%m-%dT%H:%M'),
            'expected_payment_date': forms.DateInput(attrs={'type': 'date', 'class': TW}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial.setdefault('sale_date', __import__('django.utils.timezone', fromlist=['now']).now().strftime('%Y-%m-%dT%H:%M'))

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


class DebtReturnForm(forms.ModelForm):
    class Meta:
        model = DebtReturn
        fields = ['debt', 'amount', 'return_date', 'payment_method', 'comment']
        widgets = {
            'debt': forms.HiddenInput(),
            'amount': forms.NumberInput(attrs={'class': TW}),
            'return_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}, format='%Y-%m-%dT%H:%M'),
            'payment_method': forms.Select(attrs={'class': TW}),
            'comment': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 1}),
        }

    def __init__(self, *args, debt=None, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        if not self.instance.pk:
            self.initial.setdefault('return_date', timezone.now().strftime('%Y-%m-%dT%H:%M'))
        if debt:
            self.fields['debt'].initial = debt.pk
            self.initial.setdefault('amount', debt.balance)

    def clean(self):
        cleaned_data = super().clean()
        debt = cleaned_data.get('debt')
        amount = cleaned_data.get('amount')
        if debt and amount and amount > debt.balance:
            raise ValidationError(
                f'Repayment amount exceeds outstanding balance of TZS {debt.balance:,.0f}'
            )
        return cleaned_data
