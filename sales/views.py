from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Count
from django.db.models.functions import Coalesce
from .models import Sale, ReturnInward
from .forms import SaleForm, ReturnInwardForm

_DEC = DecimalField(max_digits=15, decimal_places=2)


class SaleListView(ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 50

    def get_queryset(self):
        queryset = Sale.objects.select_related(
            'product_spec__product', 
            'product_spec__spec_value',
            'payment_method'
        ).all()
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        product = self.request.GET.get('product')

        if date_from:
            queryset = queryset.filter(sale_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(sale_date__date__lte=date_to)
        if product:
            queryset = queryset.filter(product_spec__product__name__icontains=product)

        return queryset.order_by('-sale_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate summary statistics for the filtered queryset
        qs = self.get_queryset()
        
        # Total count and amount
        total_count = qs.count()
        amount_expr = ExpressionWrapper(F('quantity') * F('unit_price') - F('discount'), output_field=_DEC)
        total_amount = qs.aggregate(total=Coalesce(Sum(amount_expr), Decimal('0')))['total']
        
        # Average transaction
        avg_amount = total_amount / total_count if total_count > 0 else Decimal('0')
        
        # Calculate total profit (amount - cost)
        cost_expr = ExpressionWrapper(F('quantity') * F('product_spec__cached_wac'), output_field=_DEC)
        total_profit = qs.aggregate(
            profit=Coalesce(Sum(amount_expr - cost_expr), Decimal('0'))
        )['profit']
        
        context['stats'] = {
            'total_count': total_count,
            'total_amount': total_amount,
            'avg_amount': avg_amount,
            'total_profit': total_profit,
        }
        
        # Provide create URL from model method if available, otherwise fallback
        try:
            from .models import Sale
            context['create_url'] = reverse_lazy('sales:sale_create_partial')
        except:
            context['create_url'] = '/sales/new/'
        
        return context


class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:sale_list')

    def _get_spec(self):
        spec_id = self.request.GET.get('product_spec') or self.request.POST.get('product_spec')
        if spec_id:
            try:
                from catalog.models import ProductSpec
                return ProductSpec.objects.select_related(
                    'product', 'product__brand', 'spec_value'
                ).get(pk=spec_id)
            except Exception:
                pass
        return None

    def get_initial(self):
        initial = super().get_initial()
        spec = self._get_spec()
        if spec:
            initial['product_spec'] = spec.pk
            price = spec.default_selling_price or spec.cached_wac or None
            if price:
                initial['unit_price'] = price
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        spec = self._get_spec()
        if spec:
            price = spec.default_selling_price or spec.cached_wac or None
            context['prefill_spec'] = {
                'id': spec.pk,
                'label': str(spec),
                'stock': spec.current_stock,
                'selling_price': str(price or ''),
                'cost_price': str(spec.cached_wac or ''),
            }
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Sale recorded.')
        return super().form_valid(form)


class ReturnInwardCreateView(CreateView):
    model = ReturnInward
    form_class = ReturnInwardForm
    template_name = 'sales/return_inward_form.html'
    success_url = reverse_lazy('sales:sale_list')

    def form_valid(self, form):
        messages.success(self.request, 'Return inward recorded.')
        return super().form_valid(form)


def sale_create_partial(request):
    """HTMX: return sale form panel."""
    form = SaleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if request.headers.get('HX-Request'):
            return render(request, 'sales/_sale_panel_success.html', {})
        return redirect('sales:sale_list')
    return render(request, 'sales/_sale_panel.html', {'form': form})


def sale_return_partial(request, pk):
    """HTMX: return inward form pre-filled with sale."""
    sale = get_object_or_404(Sale, pk=pk)
    form = ReturnInwardForm(request.POST or None, initial={
        'product_spec': sale.product_spec,
        'unit_price': sale.unit_price,
    })
    if request.method == 'POST' and form.is_valid():
        form.save()
        if request.headers.get('HX-Request'):
            return render(request, 'sales/_return_success.html', {'sale': sale})
        return redirect('sales:sale_list')
    template = 'sales/_return_form.html' if request.headers.get('HX-Request') else 'sales/return_inward_form.html'
    return render(request, template, {'form': form, 'sale': sale})


def index(request):
    from django.shortcuts import redirect
    return redirect('sales:sale_list')


class SaleDetailView(DetailView):
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'

    def get_queryset(self):
        return Sale.objects.select_related(
            'product_spec__product', 'product_spec__spec_value',
            'product_spec__product__brand', 'payment_method'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale = self.object
        context['returns'] = sale.returns.order_by('-sale_date')
        context['profit'] = sale.get_profit_amount()
        context['profit_margin'] = sale.get_profit_margin_percent()
        context['remaining_qty'] = sale.get_remaining_quantity()
        return context


class SaleUpdateView(UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_update.html'
    context_object_name = 'sale'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Sale updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        spec = self.object.product_spec
        context['prefill_spec'] = {
            'id': spec.pk,
            'label': str(spec),
            'stock': spec.current_stock,
            'selling_price': str(spec.default_selling_price or ''),
            'cost_price': str(spec.default_cost_price or ''),
        }
        return context


class SaleDeleteView(DeleteView):
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    context_object_name = 'sale'
    success_url = reverse_lazy('sales:sale_list')

    def get_queryset(self):
        # Only allow deletion if no returns exist
        return Sale.objects.filter(returns__isnull=True)

    def form_valid(self, form):
        messages.success(self.request, f'Sale #{self.object.pk} deleted.')
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        sale = get_object_or_404(Sale, pk=kwargs['pk'])
        if sale.returns.exists():
            messages.error(request, 'Cannot delete a sale that has returns.')
            return redirect(sale.get_absolute_url())
        return super().get(request, *args, **kwargs)

# Create your views here.
