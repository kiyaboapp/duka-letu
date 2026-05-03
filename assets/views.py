from decimal import Decimal
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.db.models.functions import Coalesce
from .models import Asset, AssetCategory
from .forms import AssetForm, AssetDisposalForm


def index(request):
    assets = Asset.objects.select_related('asset_type__category').filter(disposal_date__isnull=True)
    total_cost = sum(a.effective_cost for a in assets)
    total_acc_dep = sum(a.accumulated_depreciation for a in assets)
    total_nbv = total_cost - total_acc_dep

    # Group by category
    categories = {}
    for a in assets:
        cat = a.asset_type.category.name
        categories.setdefault(cat, []).append(a)

    return render(request, 'assets/index.html', {
        'assets': assets,
        'categories': categories,
        'total_cost': total_cost,
        'total_acc_dep': total_acc_dep,
        'total_nbv': total_nbv,
    })


def asset_detail(request, pk):
    asset = get_object_or_404(Asset.objects.select_related('asset_type__category'), pk=pk)

    # Build depreciation schedule year by year
    schedule = []
    if asset.depreciation_method != 'NONE' and asset.effective_cost:
        depreciable = asset.effective_cost - asset.residual_value
        acc = Decimal('0')
        year = asset.acquisition_date.year
        nbv = asset.effective_cost
        while acc < depreciable and year <= asset.acquisition_date.year + 50:
            if asset.depreciation_method == 'SL':
                charge = (depreciable * asset.depreciation_rate).quantize(Decimal('0.01'))
            else:  # DB
                charge = (nbv * asset.depreciation_rate).quantize(Decimal('0.01'))
            charge = min(charge, depreciable - acc)
            acc += charge
            nbv = asset.effective_cost - acc
            schedule.append({'year': year, 'charge': charge, 'acc_dep': acc, 'nbv': max(nbv, Decimal('0'))})
            year += 1
            if acc >= depreciable:
                break

    return render(request, 'assets/asset_detail.html', {
        'asset': asset,
        'schedule': schedule,
    })


def asset_create(request):
    form = AssetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        asset = form.save()
        return redirect('assets:asset_detail', pk=asset.pk)
    return render(request, 'assets/asset_form.html', {'form': form, 'title': 'Add Asset'})


def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    is_htmx = request.headers.get('HX-Request')
    form = AssetForm(request.POST or None, instance=asset)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if is_htmx:
            asset.refresh_from_db()
            return render(request, 'assets/_asset_info.html', {'asset': asset})
        return redirect('assets:asset_detail', pk=pk)
    template = 'assets/_asset_edit_form.html' if is_htmx else 'assets/asset_form.html'
    return render(request, template, {'form': form, 'asset': asset, 'title': 'Edit Asset'})


def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        return redirect('assets:index')
    return render(request, 'assets/asset_confirm_delete.html', {'asset': asset})


def asset_disposal(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    is_htmx = request.headers.get('HX-Request')
    form = AssetDisposalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        asset.disposal_date = form.cleaned_data['disposal_date']
        asset.disposal_proceeds = form.cleaned_data['disposal_proceeds']
        if form.cleaned_data.get('notes'):
            asset.notes = (asset.notes + '\n' + form.cleaned_data['notes']).strip()
        asset.save(update_fields=['disposal_date', 'disposal_proceeds', 'notes'])
        if is_htmx:
            asset.refresh_from_db()
            return render(request, 'assets/_asset_info.html', {'asset': asset})
        return redirect('assets:asset_detail', pk=pk)
    template = 'assets/_asset_disposal_form.html' if is_htmx else 'assets/asset_form.html'
    return render(request, template, {'form': form, 'asset': asset})
