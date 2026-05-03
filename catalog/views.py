from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Sum, F, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from .models import ProductSpec, Product, Category, Brand, ProductType
from sales.models import Sale, SaleOfficeUse, Drawing, ReturnInward
from inventory.models import PurchaseDetail, ReturnOutward
from credit.models import Debt


class ProductSpecListView(ListView):
    """
    Professional product master data view.
    Searchable grid with filters, sorting, and row-level actions.
    """
    model = ProductSpec
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 50

    def get_queryset(self):
        queryset = ProductSpec.objects.select_related(
            'product', 'product__product_type', 'product__product_type__category',
            'product__brand', 'spec_value', 'product__unit'
        ).annotate(
            total_purchased=Coalesce(Sum('purchase_details__quantity'), 0, output_field=IntegerField()),
            total_sold=Coalesce(Sum('sales__quantity'), 0, output_field=IntegerField()),
        )

        # Search filter
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search) |
                Q(product__product_type__name__icontains=search) |
                Q(product__brand__name__icontains=search) |
                Q(spec_value__value__icontains=search) |
                Q(product__product_type__category__name__icontains=search)
            )

        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(product__product_type__category_id=category_id)

        # Brand filter
        brand_id = self.request.GET.get('brand')
        if brand_id:
            queryset = queryset.filter(product__brand_id=brand_id)

        # Stock status filter
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'out':
            queryset = queryset.filter(current_stock__lte=0)
        elif stock_status == 'low':
            queryset = queryset.filter(current_stock__gt=0, current_stock__lte=F('reorder_level'))
        elif stock_status == 'ok':
            queryset = queryset.filter(current_stock__gt=F('reorder_level'))

        # Sorting
        sort_by = self.request.GET.get('sort', 'name')
        sort_order = self.request.GET.get('order', 'asc')
        sort_fields = {
            'name': 'product__name',
            'stock': 'current_stock',
            'cost': 'default_cost_price',
            'price': 'default_selling_price',
            'category': 'product__product_type__category__name',
        }
        if sort_by in sort_fields:
            field = sort_fields[sort_by]
            if sort_order == 'desc':
                field = '-' + field
            queryset = queryset.order_by(field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'brand': self.request.GET.get('brand', ''),
            'stock_status': self.request.GET.get('stock_status', ''),
            'sort': self.request.GET.get('sort', 'name'),
            'order': self.request.GET.get('order', 'asc'),
        }
        context['total_count'] = self.get_queryset().count()
        return context


class ProductSpecDetailView(DetailView):
    """
    360-degree product view.
    Shows all related data: transactions, stock movements, history.
    """
    model = ProductSpec
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return ProductSpec.objects.select_related(
            'product', 'product__product_type', 'product__product_type__category',
            'product__brand', 'spec_value', 'product__unit'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_spec = self.object

        # Recent transactions (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Sales history
        context['recent_sales'] = Sale.objects.filter(
            product_spec=product_spec,
            sale_date__gte=thirty_days_ago
        ).select_related('payment_method').order_by('-sale_date')[:20]

        # Purchase history
        context['recent_purchases'] = PurchaseDetail.objects.filter(
            product_spec=product_spec,
            purchase__purchase_date__gte=thirty_days_ago
        ).select_related('purchase', 'purchase__supplier').order_by('-purchase__purchase_date')[:20]

        # Credit sales
        context['recent_credit'] = Debt.objects.filter(
            product_spec=product_spec,
            sale_date__gte=thirty_days_ago
        ).select_related('debtor').order_by('-sale_date')[:10]

        # Office use
        context['recent_office_use'] = SaleOfficeUse.objects.filter(
            product_spec=product_spec,
            sale_date__gte=thirty_days_ago
        ).select_related('office_use_category').order_by('-sale_date')[:10]

        # Stock movement summary (last 90 days)
        ninety_days_ago = timezone.now() - timedelta(days=90)

        _DEC = DecimalField(max_digits=15, decimal_places=2)
        context['stock_summary'] = {
            'purchased': PurchaseDetail.objects.filter(
                product_spec=product_spec,
                purchase__purchase_date__gte=ninety_days_ago
            ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0'), output_field=_DEC))['total'],
            'sold': Sale.objects.filter(
                product_spec=product_spec,
                sale_date__gte=ninety_days_ago
            ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0'), output_field=_DEC))['total'],
            'credit': Debt.objects.filter(
                product_spec=product_spec,
                sale_date__gte=ninety_days_ago
            ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0'), output_field=_DEC))['total'],
            'office_use': SaleOfficeUse.objects.filter(
                product_spec=product_spec,
                sale_date__gte=ninety_days_ago
            ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0'), output_field=_DEC))['total'],
            'drawings': Drawing.objects.filter(
                product_spec=product_spec,
                sale_date__gte=ninety_days_ago
            ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0'), output_field=_DEC))['total'],
        }

        # Related products (same type or category, different spec)
        context['related_products'] = ProductSpec.objects.filter(
            product=product_spec.product
        ).exclude(pk=product_spec.pk).select_related('spec_value')[:10]

        # Financial summary
        context['financials'] = {
            'avg_cost': product_spec.default_cost_price or Decimal('0'),
            'avg_price': product_spec.default_selling_price or Decimal('0'),
            'stock_value': (product_spec.default_cost_price or Decimal('0')) * product_spec.current_stock,
        }

        return context


def index(request):
    """Redirect to professional product list."""
    return redirect('catalog:product_list')


def product_sell_partial(request, pk):
    """HTMX: return sale form pre-filled with this product."""
    from sales.forms import SaleForm
    spec = get_object_or_404(ProductSpec, pk=pk)
    form = SaleForm(initial={
        'product_spec': spec.pk,
        'unit_price': spec.default_selling_price,
    })
    return render(request, 'catalog/_sell_form.html', {'form': form, 'spec': spec})


def product_purchase_partial(request, pk):
    """HTMX: return purchase form pre-filled with this product."""
    from inventory.forms import PurchaseDetailForm
    spec = get_object_or_404(ProductSpec, pk=pk)
    form = PurchaseDetailForm(initial={
        'product_spec': spec.pk,
        'unit_cost': spec.default_cost_price,
    })
    return render(request, 'catalog/_purchase_form.html', {'form': form, 'spec': spec})


def product_credit_sale_partial(request, pk):
    """HTMX: return credit sale form pre-filled with this product."""
    from credit.forms import DebtForm
    spec = get_object_or_404(ProductSpec, pk=pk)
    form = DebtForm(initial={
        'product_spec': spec.pk,
        'unit_price': spec.default_selling_price,
    })
    return render(request, 'catalog/_credit_sale_form.html', {'form': form, 'spec': spec})


def product_spec_search(request):
    """
    JSON API: search product specs by name/brand/spec.
    Used by sale and purchase forms for live product lookup.
    Returns id, label, stock, cost_price, selling_price.
    """
    from django.http import JsonResponse
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 1:
        qs = ProductSpec.objects.select_related(
            'product', 'product__brand', 'spec_value'
        ).filter(
            Q(product__name__icontains=q) |
            Q(product__brand__name__icontains=q) |
            Q(spec_value__value__icontains=q)
        ).order_by('product__name', 'spec_value__value')[:30]
        for ps in qs:
            brand = ps.product.brand.name if ps.product.brand else ''
            label = ps.product.name
            if brand:
                label = f"{label} ({brand})"
            label = f"{label} — {ps.spec_value.value}"
            results.append({
                'id': ps.pk,
                'label': label,
                'stock': ps.current_stock,
                'cost_price': str(ps.default_cost_price or ''),
                'selling_price': str(ps.default_selling_price or ''),
            })
    return JsonResponse({'results': results})

