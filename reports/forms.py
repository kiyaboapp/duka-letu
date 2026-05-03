from django import forms
from reports.periods import PRESET_CHOICES, ReportPeriod


class ReportPeriodForm(forms.Form):
    preset = forms.ChoiceField(
        choices=PRESET_CHOICES, initial='this_month', required=False,
        widget=forms.Select(attrs={'class': 'form-select text-sm', 'id': 'id_preset'})
    )
    start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input text-sm', 'id': 'id_start'})
    )
    end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input text-sm', 'id': 'id_end'})
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('preset') == 'custom':
            if not cleaned.get('start'):
                self.add_error('start', 'Required for custom range.')
            if not cleaned.get('end'):
                self.add_error('end', 'Required for custom range.')
        return cleaned

    def resolved_period(self, default_preset='this_month'):
        if not self.is_valid():
            return ReportPeriod.resolve(default_preset=default_preset)
        return ReportPeriod.resolve(
            preset=self.cleaned_data.get('preset'),
            start=self.cleaned_data.get('start'),
            end=self.cleaned_data.get('end'),
            default_preset=default_preset,
        )
