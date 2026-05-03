from django import forms
from django.utils import timezone
from .models import ExpenseItem, ExpenseRate, Payment, LiabilityPaymentDetail, LiabilityItem, PaymentMethod


class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ['expense_type', 'name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ExpenseRateForm(forms.ModelForm):
    class Meta:
        model = ExpenseRate
        fields = ['amount', 'effective_from', 'change_reason']
        widgets = {'effective_from': forms.DateInput(attrs={'type': 'date'})}


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_method', 'payment_date', 'description']
        widgets = {
            'payment_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            category_link__is_active=True
        ).order_by('name')
        if not self.instance.pk:
            self.initial.setdefault('payment_date', timezone.now().strftime('%Y-%m-%dT%H:%M'))
            cash = PaymentMethod.objects.filter(name__iexact='cash').values_list('pk', flat=True).first()
            if cash:
                self.initial.setdefault('payment_method', cash)


class LiabilityPaymentForm(forms.Form):
    principal_amount = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0)
    interest_amount = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0, initial=0)
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(), empty_label='Select method'
    )
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('payment_date'):
            self.initial['payment_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def save(self, liability: LiabilityItem):
        from .models import Payment
        payment = Payment.objects.create(
            payment_type='LIABILITY',
            liability_item=liability,
            amount_paid=self.cleaned_data['principal_amount'] + self.cleaned_data['interest_amount'],
            payment_method=self.cleaned_data['payment_method'],
            payment_date=self.cleaned_data['payment_date'],
            description=self.cleaned_data.get('description', ''),
        )
        LiabilityPaymentDetail.objects.create(
            payment=payment,
            liability_item=liability,
            principal_amount=self.cleaned_data['principal_amount'],
            interest_amount=self.cleaned_data['interest_amount'],
            balance_after_payment=liability.current_balance - self.cleaned_data['principal_amount'],
        )
        return payment
