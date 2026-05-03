from django import forms
from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_type', 'name', 'cost_price', 'acquisition_date',
            'depreciation_method', 'depreciation_rate', 'residual_value', 'notes',
        ]
        widgets = {
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        asset = super().save(commit=False)
        # Keep worth in sync with cost_price
        asset.worth = asset.cost_price
        if commit:
            asset.save()
        return asset


class AssetDisposalForm(forms.Form):
    disposal_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    disposal_proceeds = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0, initial=0)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
