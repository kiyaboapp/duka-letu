from django.shortcuts import render
from catalog.models import ProductSpec


def low_stock(request):
    specs = ProductSpec.objects.select_related('product', 'spec_value').all()
    low = [s for s in specs if s.is_low_stock]
    out = [s for s in specs if s.is_out_of_stock]
    return render(request, 'reports/low_stock.html', {'low_stock': low, 'out_of_stock': out})
