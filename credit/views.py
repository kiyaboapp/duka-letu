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


def index(request):
    return render(request, 'credit/index.html')

# Create your views here.
