from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Count
from django.db.models.functions import Coalesce
from .models import Purchase, PurchaseDetail, Supplier, ReturnOutward
from .forms import PurchaseForm, PurchaseDetailFormSet, ReturnOutwardForm

_DEC = DecimalField(max_digits=15, decimal_places=2)


class PurchaseListView(ListView):
    model = Purchase
    template_name = 'inventory/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 50

    def get_queryset(self):
        return Purchase.objects.select_related('supplier').all().order_by('-purchase_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate summary statistics
        qs = self.get_queryset()
        total_count = qs.count()
        total_amount = sum(p.total_amount for p in qs)
        avg_amount = total_amount / total_count if total_count > 0 else Decimal('0')
        supplier_count = qs.values('supplier').distinct().count()
        
        context['stats'] = {
            'total_count': total_count,
            'total_amount': total_amount,
            'avg_amount': avg_amount,
            'supplier_count': supplier_count,
        }
        
        context['create_url'] = reverse_lazy('inventory:purchase_create')
        
        return context


class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'inventory/purchase_form.html'
    success_url = reverse_lazy('inventory:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PurchaseDetailFormSet(self.request.POST)
        else:
            context['formset'] = PurchaseDetailFormSet()
        # Pre-load spec data if coming from product detail
        spec_id = self.request.GET.get('product_spec')
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
                    'cost_price': str(spec.default_cost_price or ''),
                    'selling_price': str(spec.default_selling_price or ''),
                }
            except Exception:
                pass
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            for detail_form in formset:
                if detail_form.cleaned_data and not detail_form.cleaned_data.get('DELETE'):
                    detail = detail_form.save(commit=False)
                    detail.purchase = self.object
                    detail.save()
            messages.success(self.request, 'Purchase recorded successfully.')
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


def index(request):
    return render(request, 'inventory/index.html')


class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_queryset(self):
        return Supplier.objects.annotate(purchase_count=Count('purchases')).order_by('name')


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object
        context['purchases'] = supplier.purchases.prefetch_related('details').order_by('-purchase_date')[:20]
        context['total_spent'] = sum(p.total_amount for p in supplier.purchases.all())
        context['purchase_count'] = supplier.purchases.count()
        context['last_purchase'] = supplier.purchases.order_by('-purchase_date').first()
        return context


class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'inventory/purchase_detail.html'
    context_object_name = 'purchase'

    def get_queryset(self):
        return Purchase.objects.select_related('supplier').prefetch_related(
            'details__product_spec__product',
            'details__product_spec__spec_value',
            'details__returns',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchase = self.object
        context['return_form'] = ReturnOutwardForm()
        context['total_with_freight'] = purchase.total_amount + purchase.carriage_inwards
        return context


class PurchaseUpdateView(UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'inventory/purchase_update.html'
    context_object_name = 'purchase'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Purchase updated successfully.')
        return super().form_valid(form)


class PurchaseDeleteView(DeleteView):
    model = Purchase
    template_name = 'inventory/purchase_confirm_delete.html'
    context_object_name = 'purchase'
    success_url = reverse_lazy('inventory:index')

    def get(self, request, *args, **kwargs):
        purchase = get_object_or_404(Purchase, pk=kwargs['pk'])
        from .models import ReturnOutward
        if ReturnOutward.objects.filter(purchase_detail__purchase=purchase).exists():
            messages.error(request, 'Cannot delete a purchase that has return outwards.')
            return redirect(purchase.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'Purchase #{self.object.pk} deleted.')
        return super().form_valid(form)


class ReturnOutwardCreateView(CreateView):
    model = ReturnOutward
    form_class = ReturnOutwardForm
    template_name = 'inventory/return_outward_form.html'
    success_url = reverse_lazy('inventory:index')

    def get_initial(self):
        initial = super().get_initial()
        purchase_id = self.request.GET.get('purchase')
        if purchase_id:
            initial['purchase_id'] = purchase_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchase_id = self.request.GET.get('purchase')
        if purchase_id:
            context['purchase'] = get_object_or_404(
                Purchase.objects.select_related('supplier').prefetch_related('details__product_spec__product'),
                pk=purchase_id
            )
            # Limit form choices to this purchase's details
            context['form'].fields['purchase_detail'].queryset = PurchaseDetail.objects.filter(
                purchase_id=purchase_id
            ).select_related('product_spec__product')
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Return outward recorded.')
        ret = form.save()
        return redirect(ret.purchase_detail.purchase.get_absolute_url())

# Create your views here.
