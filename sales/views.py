from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import Sale, ReturnInward
from .forms import SaleForm, ReturnInwardForm


class SaleListView(ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 50

    def get_queryset(self):
        queryset = Sale.objects.select_related('product_spec__product').all()
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        product = self.request.GET.get('product')

        if date_from:
            queryset = queryset.filter(sale_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(sale_date__date__lte=date_to)
        if product:
            queryset = queryset.filter(product_spec__product__name__icontains=product)

        return queryset


class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pre-load spec data if coming from product detail
        spec_id = self.request.GET.get('product_spec') or self.request.POST.get('product_spec')
        if spec_id:
            try:
                from catalog.models import ProductSpec
                spec = ProductSpec.objects.select_related(
                    'product', 'product__brand', 'spec_value'
                ).get(pk=spec_id)
                context['prefill_spec'] = {
                    'id': spec.pk,
                    'label': str(spec),
                    'stock': spec.current_stock,
                    'selling_price': str(spec.default_selling_price or ''),
                    'cost_price': str(spec.default_cost_price or ''),
                }
            except Exception:
                pass
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


def index(request):
    from django.shortcuts import redirect
    return redirect('sales:sale_list')

# Create your views here.
