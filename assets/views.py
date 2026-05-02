from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import Asset


def index(request):
    assets = Asset.objects.select_related('asset_type__category').order_by('asset_type__category__name', 'name')
    total_assets = assets.count()
    total_book_value = assets.aggregate(total=Coalesce(Sum('worth'), Decimal('0')))['total']

    return render(request, 'assets/index.html', {
        'assets': assets,
        'total_assets': total_assets,
        'total_book_value': total_book_value,
    })
