from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Debtor, Debt, DebtReturn
from .forms import DebtorForm, DebtForm, DebtReturnForm


class DebtorListView(ListView):
    model = Debtor
    template_name = 'credit/debtor_list.html'
    context_object_name = 'debtors'
    paginate_by = 50


class DebtorDetailView(DetailView):
    model = Debtor
    template_name = 'credit/debtor_detail.html'
    context_object_name = 'debtor'


class DebtorCreateView(CreateView):
    model = Debtor
    form_class = DebtorForm
    template_name = 'credit/debtor_form.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            # append new debtor pk so the credit form can pre-select it
            from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
            parsed = urlparse(next_url)
            params = parse_qs(parsed.query)
            params['debtor'] = [str(self.object.pk)]
            new_query = urlencode({k: v[0] for k, v in params.items()})
            return urlunparse(parsed._replace(query=new_query))
        return reverse_lazy('credit:index')


class DebtCreateView(CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'credit/debt_form.html'
    success_url = reverse_lazy('credit:index')

    def get_initial(self):
        initial = super().get_initial()
        spec_id = self.request.GET.get('product_spec')
        debtor_id = self.request.GET.get('debtor')
        if spec_id:
            try:
                from catalog.models import ProductSpec
                spec = ProductSpec.objects.select_related('product', 'spec_value').get(pk=spec_id)
                initial['product_spec'] = spec.pk
                price = spec.default_selling_price or spec.cached_wac or None
                if price:
                    initial['unit_price'] = price
            except Exception:
                pass
        if debtor_id:
            initial['debtor'] = debtor_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        spec_id = self.request.GET.get('product_spec')
        debtor_id = self.request.GET.get('debtor')
        if spec_id:
            try:
                from catalog.models import ProductSpec
                spec = ProductSpec.objects.select_related('product', 'spec_value').get(pk=spec_id)
                context['spec'] = spec
                context['fill_price'] = spec.default_selling_price or spec.cached_wac
            except Exception:
                pass
        if debtor_id:
            try:
                context['selected_debtor'] = Debtor.objects.get(pk=debtor_id)
            except Exception:
                pass
        return context

    def get_success_url(self):
        debtor_id = self.request.POST.get('debtor')
        if debtor_id:
            return reverse_lazy('credit:debtor_detail', kwargs={'pk': debtor_id})
        return reverse_lazy('credit:index')

    def form_valid(self, form):
        messages.success(self.request, 'Credit sale recorded.')
        return super().form_valid(form)


class DebtReturnCreateView(CreateView):
    model = DebtReturn
    form_class = DebtReturnForm
    template_name = 'credit/debt_return_form.html'
    success_url = reverse_lazy('credit:index')

    def form_valid(self, form):
        messages.success(self.request, 'Repayment recorded successfully.')
        return super().form_valid(form)


def debtor_repay_partial(request, pk, debt_pk):
    """HTMX: return repayment form pre-filled with debt balance."""
    from django.http import HttpResponse
    debtor = get_object_or_404(Debtor, pk=pk)
    debt = get_object_or_404(Debt, pk=debt_pk, debtor=debtor)
    is_htmx = request.headers.get('HX-Request')

    if request.method == 'POST':
        form = DebtReturnForm(request.POST)
        if form.is_valid():
            ret = form.save(commit=False)
            ret.debt = debt
            ret.save()
            if is_htmx:
                debt.refresh_from_db()
                return render(request, 'credit/_debt_row.html', {'debt': debt, 'debtor': debtor})
            from django.contrib import messages
            messages.success(request, 'Repayment recorded.')
            return redirect('credit:debtor_detail', pk=pk)
    else:
        form = DebtReturnForm(debt=debt)

    template = 'credit/_repay_form.html' if is_htmx else 'credit/debt_return_form.html'
    return render(request, template, {'form': form, 'debt': debt, 'debtor': debtor})


def debtor_block_toggle(request, pk):
    """HTMX: toggle debtor blocked status."""
    debtor = get_object_or_404(Debtor, pk=pk)
    if request.method == 'POST':
        debtor.is_blocked = not debtor.is_blocked
        debtor.save(update_fields=['is_blocked'])
        if request.headers.get('HX-Request'):
            return render(request, 'credit/_block_toggle.html', {'debtor': debtor})
        return redirect('credit:debtor_detail', pk=pk)
    return redirect('credit:debtor_detail', pk=pk)


def index(request):
    return render(request, 'credit/index.html')

# Create your views here.
