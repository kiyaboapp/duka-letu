from django.shortcuts import render
from catalog.models import ProductSpec


def stock_report(request):
    products = ProductSpec.objects.select_related('product', 'spec_value').all()
    low_stock = [p for p in products if p.is_low_stock]
    out_of_stock = [p for p in products if p.is_out_of_stock]
    return render(request, 'reports/stock_report.html', {
        'products': products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    })
