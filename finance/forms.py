from django import forms
from django.utils import timezone
from .models import ExpenseItem, ExpenseRate, Payment, LiabilityPaymentDetail, LiabilityItem, PaymentMethod, RecurrencePattern

TW = 'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
TW_SELECT = TW + ' bg-white'

DUE_DAY_CHOICES = [
    ('fixed', 'Fixed day of month (1–31)'),
    ('before_end', 'Days before month end (0 = last day)'),
]


def due_day_to_dom(mode, value):
    """Convert due_day_mode + due_day_value to specific_day_of_month."""
    n = int(value)
    if mode == 'fixed':
        return n  # 1–31; 0 = last day
    else:
        return -n  # 0 = last day, -5 = 5 days before end


class RecurringExpenseForm(forms.Form):
    """Journey A — set up a recurring expense in one step."""
    expense_type = forms.ModelChoiceField(
        queryset=None, empty_label='Select type',
        widget=forms.Select(attrs={'class': TW_SELECT})
    )
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': TW, 'placeholder': 'e.g. Kodi ya Nyumba'})
    )
    amount = forms.DecimalField(
        max_digits=15, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={'class': TW, 'placeholder': 'TZS'})
    )
    recurrence_type = forms.ChoiceField(
        choices=[('MONTHLY', 'Monthly'), ('WEEKLY', 'Weekly'), ('DAILY', 'Daily')],
        widget=forms.Select(attrs={'class': TW_SELECT})
    )
    due_day_mode = forms.ChoiceField(
        choices=DUE_DAY_CHOICES,
        widget=forms.RadioSelect(),
        initial='fixed',
        label='',
    )
    due_day_value = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': TW, 'placeholder': 'e.g. 14'}),
        label='Day',
        initial=1,
    )
    every_n_days = forms.IntegerField(
        required=False, min_value=1, initial=1,
        widget=forms.NumberInput(attrs={'class': TW, 'placeholder': 'Days'}),
        label='Every N days'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ExpenseType
        self.fields['expense_type'].queryset = ExpenseType.objects.all()

    def save(self):
        from datetime import date
        today = date.today()
        data = self.cleaned_data
        item = ExpenseItem.objects.create(
            expense_type=data['expense_type'],
            name=data['name'],
            start_date=today,
            is_active=True,
        )
        ExpenseRate.objects.create(
            expense_item=item,
            amount=data['amount'],
            effective_from=today,
        )
        dom = due_day_to_dom(data['due_day_mode'], data['due_day_value'])
        freq = data.get('every_n_days') or 1
        RecurrencePattern.objects.create(
            expense_item=item,
            recurrence_type=data['recurrence_type'],
            frequency_value=freq,
            specific_day_of_month=dom,
            start_date=today,
            is_active=True,
        )
        return item


class AdhocExpenseForm(forms.Form):
    """Journey B — record a one-off payment directly."""
    expense_type = forms.ModelChoiceField(
        queryset=None, empty_label='Select type',
        widget=forms.Select(attrs={'class': TW_SELECT})
    )
    description = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': TW, 'placeholder': 'e.g. Fundi wa laptop'})
    )
    amount = forms.DecimalField(
        max_digits=15, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={'class': TW, 'placeholder': 'TZS'})
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': TW})
    )
    payment_method = forms.ModelChoiceField(
        queryset=None, empty_label='Select method',
        widget=forms.Select(attrs={'class': TW_SELECT})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ExpenseType
        self.fields['expense_type'].queryset = ExpenseType.objects.all()
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            category_link__is_active=True
        ).order_by('name')
        self.initial.setdefault('payment_date', timezone.now().date())
        cash = PaymentMethod.objects.filter(name__iexact='cash').values_list('pk', flat=True).first()
        if cash:
            self.initial.setdefault('payment_method', cash)

    def save(self):
        from datetime import date
        data = self.cleaned_data
        today = date.today()
        item = ExpenseItem.objects.create(
            expense_type=data['expense_type'],
            name=data['description'],
            start_date=data['payment_date'],
            end_date=data['payment_date'],
            is_active=False,  # one-off, no ongoing tracking
        )
        ExpenseRate.objects.create(
            expense_item=item,
            amount=data['amount'],
            effective_from=data['payment_date'],
        )
        Payment.objects.create(
            expense_item=item,
            payment_type='EXPENSE',
            amount_paid=data['amount'],
            payment_method=data['payment_method'],
            payment_date=data['payment_date'],
        )
        return item


class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ['expense_type', 'name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': TW}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': TW}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': TW}),
            'name': forms.TextInput(attrs={'class': TW}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense_type'].widget.attrs['class'] = TW_SELECT


class ExpenseRateForm(forms.ModelForm):
    class Meta:
        model = ExpenseRate
        fields = ['amount', 'effective_from', 'change_reason']
        widgets = {
            'effective_from': forms.DateInput(attrs={'type': 'date', 'class': TW}),
            'change_reason': forms.Textarea(attrs={'rows': 2, 'class': TW}),
            'amount': forms.NumberInput(attrs={'class': TW}),
        }


class RecurrencePatternForm(forms.ModelForm):
    due_day_mode = forms.ChoiceField(
        choices=DUE_DAY_CHOICES,
        widget=forms.RadioSelect(),
        initial='fixed',
        label='',
    )
    due_day_value = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': TW, 'placeholder': 'e.g. 14'}),
        label='Day',
        initial=1,
    )
    pay_now = forms.BooleanField(required=False, label='Pay immediately')
    payment_method = forms.ModelChoiceField(
        queryset=None, required=False, label='Payment method',
        widget=forms.Select(attrs={'class': TW_SELECT})
    )

    class Meta:
        model = RecurrencePattern
        fields = ['recurrence_type', 'frequency_value', 'start_date', 'end_date']
        widgets = {
            'recurrence_type': forms.Select(attrs={'class': TW_SELECT}),
            'frequency_value': forms.NumberInput(attrs={'class': TW}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': TW}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': TW}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            category_link__is_active=True
        ).order_by('name')
        if self.instance and self.instance.pk:
            dom = self.instance.specific_day_of_month
            if dom >= 0:
                self.initial['due_day_mode'] = 'fixed'
                self.initial['due_day_value'] = dom
            else:
                self.initial['due_day_mode'] = 'before_end'
                self.initial['due_day_value'] = abs(dom)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.specific_day_of_month = due_day_to_dom(
            self.cleaned_data['due_day_mode'],
            self.cleaned_data['due_day_value'],
        )
        if commit:
            instance.save()
        return instance


class AdhocPayForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0,
                                widget=forms.NumberInput(attrs={'class': TW}))
    payment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': TW}))
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(category_link__is_active=True).order_by('name'),
        widget=forms.Select(attrs={'class': TW_SELECT})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cash = PaymentMethod.objects.filter(name__iexact='cash').values_list('pk', flat=True).first()
        if cash:
            self.initial.setdefault('payment_method', cash)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_method', 'payment_date']
        widgets = {
            'payment_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': TW},
                format='%Y-%m-%dT%H:%M'
            ),
            'amount_paid': forms.NumberInput(attrs={'class': TW}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            category_link__is_active=True
        ).order_by('name')
        self.fields['payment_method'].widget.attrs['class'] = TW_SELECT
        if not self.instance.pk:
            self.initial.setdefault('payment_date', timezone.now().strftime('%Y-%m-%dT%H:%M'))
            cash = PaymentMethod.objects.filter(name__iexact='cash').values_list('pk', flat=True).first()
            if cash:
                self.initial.setdefault('payment_method', cash)


class LiabilityPaymentForm(forms.Form):
    principal_amount = forms.DecimalField(
        max_digits=15, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={'class': TW})
    )
    interest_amount = forms.DecimalField(
        max_digits=15, decimal_places=2, min_value=0, initial=0, required=False,
        widget=forms.NumberInput(attrs={'class': TW})
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(category_link__is_active=True).order_by('name'),
        empty_label='Select method',
        widget=forms.Select(attrs={'class': TW_SELECT})
    )
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TW}, format='%Y-%m-%dT%H:%M')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('payment_date'):
            self.initial['payment_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def save(self, liability: LiabilityItem):
        interest = self.cleaned_data.get('interest_amount') or 0
        payment = Payment.objects.create(
            payment_type='LIABILITY',
            liability_item=liability,
            amount_paid=self.cleaned_data['principal_amount'] + interest,
            payment_method=self.cleaned_data['payment_method'],
            payment_date=self.cleaned_data['payment_date'],
        )
        LiabilityPaymentDetail.objects.create(
            payment=payment,
            liability_item=liability,
            principal_amount=self.cleaned_data['principal_amount'],
            interest_amount=interest,
            balance_after_payment=liability.current_balance - self.cleaned_data['principal_amount'],
        )
        return payment
