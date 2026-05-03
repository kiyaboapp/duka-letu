from django.shortcuts import render, get_object_or_404
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
    success_url = reverse_lazy('credit:index')


class DebtCreateView(CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'credit/debt_form.html'
    success_url = reverse_lazy('credit:index')

    def form_valid(self, form):
        messages.success(self.request, 'Credit sale recorded successfully.')
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
        form = DebtReturnForm(initial={'debt': debt, 'amount': debt.balance})

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
