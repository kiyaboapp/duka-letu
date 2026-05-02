from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Purchase, PurchaseDetail, Supplier
from .forms import PurchaseForm, PurchaseDetailFormSet, ReturnOutwardForm


class PurchaseListView(ListView):
    model = Purchase
    template_name = 'inventory/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 50

    def get_queryset(self):
        return Purchase.objects.select_related('supplier').all()


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

# Create your views here.
