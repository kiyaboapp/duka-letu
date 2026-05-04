from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from .models import (
    PaymentObligation, Payment, ExpenseItem, ExpenseRate,
    LiabilityItem, LiabilityPaymentDetail, PaymentMethod, RecurrencePattern,
)
from .forms import (
    ExpenseItemForm, ExpenseRateForm, PaymentForm, LiabilityPaymentForm,
    RecurrencePatternForm, RecurringExpenseForm, AdhocExpenseForm,
)
from .services import auto_generate_obligations


def index(request):
    auto_generate_obligations()
    today = timezone.now().date()
    month_start = today.replace(day=1)

    base_qs = PaymentObligation.objects.select_related(
        'expense_item__expense_type', 'liability_item'
    )

    overdue = list(base_qs.filter(status='OVERDUE', due_date__gte='2026-01-01').order_by('due_date'))
    overdue_historical = list(base_qs.filter(status='OVERDUE', due_date__lt='2026-01-01').order_by('due_date'))
    due_this_month = list(base_qs.filter(
        status__in=['PENDING', 'PARTIAL'],
        due_date__gte=today,
        due_date__year=today.year,
        due_date__month=today.month,
    ).order_by('due_date'))
    upcoming = list(base_qs.filter(
        status__in=['PENDING', 'PARTIAL'],
        due_date__gt=today,
    ).exclude(due_date__year=today.year, due_date__month=today.month).order_by('due_date'))

    paid_this_month = Payment.objects.filter(
        payment_date__date__gte=month_start,
        payment_type='EXPENSE',
    ).aggregate(total=Coalesce(Sum('amount_paid'), Decimal('0')))['total']

    from .models import Prepayment
    from django.db.models import F as _F
    unallocated_prepayments = Prepayment.objects.filter(
        status='Active', amount_utilized__lt=_F('total_prepaid')
    )

    from .models import ObligationGeneratorLog
    try:
        last_generated = ObligationGeneratorLog.objects.latest('last_run_date').last_run_date
    except ObligationGeneratorLog.DoesNotExist:
        last_generated = None

    return render(request, 'finance/index.html', {
        'overdue': overdue,
        'overdue_historical': overdue_historical,
        'due_this_month': due_this_month,
        'upcoming': upcoming,
        'paid_this_month': paid_this_month,
        'unallocated_prepayments': unallocated_prepayments,
        'last_generated': last_generated,
    })


def generate_now(request):
    if request.method == 'POST':
        auto_generate_obligations()
    return redirect('finance:index')


# ── Expense Items ─────────────────────────────────────────────────────────────

def expense_list(request):
    q = request.GET.get('q', '').strip()
    active = request.GET.get('active', '')
    today = timezone.now().date()
    month_start = today.replace(day=1)

    items = ExpenseItem.objects.select_related('expense_type').prefetch_related('rates', 'obligations')
    if q:
        items = items.filter(name__icontains=q)
    if active == '1':
        items = items.filter(is_active=True)
    elif active == '0':
        items = items.filter(is_active=False)

    from django.db.models import F
    overdue_count = PaymentObligation.objects.filter(
        expense_item__isnull=False,
        due_date__lt=today,
        amount_paid__lt=F('amount_due'),
    ).count()

    monthly_total = Payment.objects.filter(
        payment_type='EXPENSE',
        payment_date__date__gte=month_start,
    ).aggregate(total=Coalesce(Sum('amount_paid'), Decimal('0')))['total']

    return render(request, 'finance/expense_list.html', {
        'items': items, 'q': q, 'active': active,
        'today': today, 'overdue_count': overdue_count, 'monthly_total': monthly_total,
    })


def expense_detail(request, pk):
    item = get_object_or_404(ExpenseItem.objects.select_related('expense_type').prefetch_related(
        'rates', 'obligations', 'payments__payment_method', 'recurrences'
    ), pk=pk)
    today = timezone.now().date()
    obligations = item.obligations.order_by('due_date')
    overdue = [o for o in obligations if o.status == 'OVERDUE']
    pending = [o for o in obligations if o.status in ('PENDING', 'PARTIAL')]
    paid = [o for o in obligations if o.status == 'PAID']
    latest_unpaid = next((o for o in obligations.order_by('due_date') if o.balance > 0), None)
    setup_recurrence = (
        request.GET.get('setup_recurrence') == '1'
        and not item.recurrences.filter(is_active=True).exists()
        and item.end_date is None  # only for ongoing expenses
    )
    form = RecurrencePatternForm(initial={'start_date': item.start_date}) if setup_recurrence else None
    return render(request, 'finance/expense_detail.html', {
        'item': item,
        'overdue': overdue,
        'pending': pending,
        'paid': paid,
        'latest_unpaid': latest_unpaid,
        'payments': item.payments.order_by('-payment_date')[:20],
        'setup_recurrence': setup_recurrence,
        'form': form,
    })


def expense_create(request):
    """Two-path entry: choose recurring or one-off."""
    return render(request, 'finance/expense_create_choose.html')


def expense_create_recurring(request):
    form = RecurringExpenseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save()
        return redirect('finance:expense_detail', pk=item.pk)
    return render(request, 'finance/expense_create_recurring.html', {'form': form})


def expense_create_adhoc(request):
    form = AdhocExpenseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('finance:index')
    return render(request, 'finance/expense_create_adhoc.html', {'form': form})


def expense_update(request, pk):
    item = get_object_or_404(ExpenseItem, pk=pk)
    form = ExpenseItemForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('finance:expense_detail', pk=item.pk)
    return render(request, 'finance/expense_form.html', {'form': form, 'item': item, 'is_update': True})


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

    if obligation.balance <= 0:
        if is_htmx:
            return render(request, 'finance/_obligation_row.html', {'o': obligation})
        return redirect('finance:index')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.amount_paid = min(payment.amount_paid, obligation.balance)
            payment.obligation = obligation
            payment.payment_type = 'EXPENSE' if obligation.obligation_type == 'EXPENSE' else 'LIABILITY'
            payment.expense_item = obligation.expense_item
            payment.liability_item = obligation.liability_item
            payment.save()
            obligation.amount_paid = (obligation.amount_paid or Decimal('0')) + payment.amount_paid
            obligation.save(update_fields=['amount_paid', 'status'])
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


def expense_direct_pay(request, pk):
    """Record a direct payment for a one-off expense that has no obligation."""
    item = get_object_or_404(ExpenseItem, pk=pk)
    from .forms import AdhocPayForm
    form = AdhocPayForm(request.POST or None, initial={
        'amount': item.current_rate(),
        'payment_date': timezone.now().date(),
    })
    if request.method == 'POST' and form.is_valid():
        Payment.objects.create(
            expense_item=item,
            payment_type='EXPENSE',
            amount_paid=form.cleaned_data['amount'],
            payment_method=form.cleaned_data['payment_method'],
            payment_date=form.cleaned_data['payment_date'],
        )
        return redirect('finance:expense_detail', pk=pk)
    return render(request, 'finance/expense_direct_pay.html', {'item': item, 'form': form})

def recurrence_create(request, pk):
    item = get_object_or_404(ExpenseItem, pk=pk)
    form = RecurrencePatternForm(request.POST or None, initial={'start_date': item.start_date})
    if request.method == 'POST' and form.is_valid():
        pattern = form.save(commit=False)
        pattern.expense_item = item
        pattern.save()  # triggers immediate generation
        # Pay now if requested
        if form.cleaned_data.get('pay_now') and form.cleaned_data.get('payment_method'):
            obligation = PaymentObligation.objects.filter(
                expense_item=item, status__in=['PENDING', 'OVERDUE']
            ).order_by('due_date').first()
            if obligation:
                from .models import Payment
                Payment.objects.create(
                    obligation=obligation,
                    expense_item=item,
                    payment_type='EXPENSE',
                    amount_paid=obligation.balance,
                    payment_method=form.cleaned_data['payment_method'],
                )
                obligation.amount_paid = obligation.amount_due
                obligation.save(update_fields=['amount_paid', 'status'])
        if request.headers.get('HX-Request'):
            item.refresh_from_db()
            return render(request, 'finance/_recurrence_panel.html', {'item': item})
        return redirect('finance:expense_detail', pk=pk)
    if request.headers.get('HX-Request'):
        return render(request, 'finance/_recurrence_form.html', {'form': form, 'item': item})
    return render(request, 'finance/recurrence_form.html', {'form': form, 'item': item})


def recurrence_update(request, pk):
    pattern = get_object_or_404(RecurrencePattern, pk=pk)
    form = RecurrencePatternForm(request.POST or None, instance=pattern)
    if request.method == 'POST' and form.is_valid():
        form.save()  # triggers immediate generation via RecurrencePattern.save()
        if request.headers.get('HX-Request'):
            pattern.expense_item.refresh_from_db()
            return render(request, 'finance/_recurrence_panel.html', {'item': pattern.expense_item})
        return redirect('finance:expense_detail', pk=pattern.expense_item.pk)
    if request.headers.get('HX-Request'):
        return render(request, 'finance/_recurrence_form.html', {'form': form, 'item': pattern.expense_item})
    return render(request, 'finance/recurrence_form.html', {'form': form, 'item': pattern.expense_item})


def recurrence_delete(request, pk):
    pattern = get_object_or_404(RecurrencePattern, pk=pk)
    expense_pk = pattern.expense_item.pk
    if request.method == 'POST':
        # Deactivate instead of delete to preserve history
        pattern.is_active = False
        pattern.save()  # triggers future obligation cancellation via RecurrencePattern.save()
        if request.headers.get('HX-Request'):
            pattern.expense_item.refresh_from_db()
            return render(request, 'finance/_recurrence_panel.html', {'item': pattern.expense_item})
        return redirect('finance:expense_detail', pk=expense_pk)
    return redirect('finance:expense_detail', pk=expense_pk)
