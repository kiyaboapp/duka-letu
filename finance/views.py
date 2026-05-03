from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from .models import (
    PaymentObligation, Payment, ExpenseItem, ExpenseRate,
    LiabilityItem, LiabilityPaymentDetail, PaymentMethod,
)
from .forms import ExpenseItemForm, ExpenseRateForm, PaymentForm, LiabilityPaymentForm
from .services import auto_generate_obligations


def index(request):
    auto_generate_obligations()
    today = timezone.now().date()
    month_start = today.replace(day=1)

    obligations = PaymentObligation.objects.select_related(
        'expense_item__expense_type', 'liability_item'
    ).order_by('due_date')

    overdue = [o for o in obligations if o.payment_status == 'OVERDUE']
    due_this_month = [o for o in obligations if o.payment_status in ('PENDING', 'PARTIAL') and o.due_date >= today and o.due_date.month == today.month and o.due_date.year == today.year]
    upcoming = [o for o in obligations if o.payment_status in ('PENDING', 'PARTIAL') and o.due_date > today and not (o.due_date.month == today.month and o.due_date.year == today.year)]

    paid_this_month = Payment.objects.filter(
        payment_date__date__gte=month_start,
        payment_type='EXPENSE',
    ).aggregate(total=Coalesce(Sum('amount_paid'), Decimal('0')))['total']

    return render(request, 'finance/index.html', {
        'overdue': overdue,
        'due_this_month': due_this_month,
        'upcoming': upcoming,
        'paid_this_month': paid_this_month,
    })


# ── Expense Items ─────────────────────────────────────────────────────────────

def expense_list(request):
    q = request.GET.get('q', '').strip()
    active = request.GET.get('active', '')
    items = ExpenseItem.objects.select_related('expense_type').prefetch_related('rates')
    if q:
        items = items.filter(name__icontains=q)
    if active == '1':
        items = items.filter(is_active=True)
    elif active == '0':
        items = items.filter(is_active=False)
    return render(request, 'finance/expense_list.html', {'items': items, 'q': q, 'active': active})


def expense_detail(request, pk):
    item = get_object_or_404(ExpenseItem.objects.select_related('expense_type').prefetch_related(
        'rates', 'obligations', 'payments__payment_method', 'recurrences'
    ), pk=pk)
    today = timezone.now().date()
    obligations = item.obligations.order_by('due_date')
    overdue = [o for o in obligations if o.payment_status == 'OVERDUE']
    pending = [o for o in obligations if o.payment_status in ('PENDING', 'PARTIAL')]
    paid = [o for o in obligations if o.payment_status == 'PAID']
    latest_unpaid = next((o for o in obligations.order_by('due_date') if o.balance > 0), None)
    return render(request, 'finance/expense_detail.html', {
        'item': item,
        'overdue': overdue,
        'pending': pending,
        'paid': paid,
        'latest_unpaid': latest_unpaid,
        'payments': item.payments.order_by('-payment_date')[:20],
    })


def expense_create(request):
    form = ExpenseItemForm(request.POST or None)
    rate_form = ExpenseRateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and rate_form.is_valid():
        item = form.save()
        rate = rate_form.save(commit=False)
        rate.expense_item = item
        rate.save()
        return redirect('finance:expense_detail', pk=item.pk)
    return render(request, 'finance/expense_form.html', {'form': form, 'rate_form': rate_form})


def expense_rate_create(request, pk):
    item = get_object_or_404(ExpenseItem, pk=pk)
    form = ExpenseRateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rate = form.save(commit=False)
        rate.expense_item = item
        rate.save()
        if request.headers.get('HX-Request'):
            rates = item.rates.order_by('-effective_from')
            return render(request, 'finance/_rate_rows.html', {'item': item, 'rates': rates})
        return redirect('finance:expense_detail', pk=pk)
    if request.headers.get('HX-Request'):
        return render(request, 'finance/_rate_form.html', {'form': form, 'item': item})
    return render(request, 'finance/rate_form.html', {'form': form, 'item': item})


def expense_toggle(request, pk):
    item = get_object_or_404(ExpenseItem, pk=pk)
    if request.method == 'POST':
        item.is_active = not item.is_active
        item.save(update_fields=['is_active'])
        if request.headers.get('HX-Request'):
            return render(request, 'finance/_expense_toggle.html', {'item': item})
        return redirect('finance:expense_detail', pk=pk)
    return redirect('finance:expense_detail', pk=pk)


# ── Obligation Pay ────────────────────────────────────────────────────────────

def obligation_pay(request, pk):
    obligation = get_object_or_404(PaymentObligation.objects.select_related(
        'expense_item', 'liability_item'
    ), pk=pk)
    is_htmx = request.headers.get('HX-Request')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.obligation = obligation
            payment.payment_type = 'EXPENSE' if obligation.obligation_type == 'EXPENSE' else 'LIABILITY'
            payment.expense_item = obligation.expense_item
            payment.liability_item = obligation.liability_item
            payment.save()
            obligation.amount_paid = (obligation.amount_paid or Decimal('0')) + payment.amount_paid
            obligation.save(update_fields=['amount_paid'])
            if is_htmx:
                return render(request, 'finance/_obligation_row.html', {'o': obligation})
            return redirect('finance:index')
    else:
        form = PaymentForm(initial={'amount_paid': obligation.balance})

    template = 'finance/_obligation_pay_form.html' if is_htmx else 'finance/payment_form.html'
    return render(request, template, {'form': form, 'obligation': obligation})


# ── Liabilities ───────────────────────────────────────────────────────────────

def liability_list(request):
    liabilities = LiabilityItem.objects.filter(is_active=True).select_related(
        'liability_type__category'
    ).prefetch_related('payment_details')
    return render(request, 'finance/liability_list.html', {'liabilities': liabilities})


def liability_detail(request, pk):
    liability = get_object_or_404(LiabilityItem.objects.select_related(
        'liability_type__category'
    ).prefetch_related('payment_details__payment__payment_method'), pk=pk)
    return render(request, 'finance/liability_detail.html', {'liability': liability})


def liability_pay(request, pk):
    liability = get_object_or_404(LiabilityItem, pk=pk)
    is_htmx = request.headers.get('HX-Request')

    if request.method == 'POST':
        form = LiabilityPaymentForm(request.POST)
        if form.is_valid():
            form.save(liability)
            if is_htmx:
                liability.refresh_from_db()
                return render(request, 'finance/_liability_balance.html', {'liability': liability})
            return redirect('finance:liability_detail', pk=pk)
    else:
        form = LiabilityPaymentForm(initial={
            'principal_amount': min(liability.amount_per_return or Decimal('0'), liability.current_balance),
            'interest_amount': Decimal('0'),
        })

    template = 'finance/_liability_pay_form.html' if is_htmx else 'finance/liability_payment_form.html'
    return render(request, template, {'form': form, 'liability': liability})
