from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from reports.models import ReportSnapshot


def snapshot_list(request):
    snapshots = ReportSnapshot.objects.order_by('-period_end')
    return render(request, 'reports/snapshot_list.html', {'snapshots': snapshots})


def snapshot_detail(request, pk):
    snap = get_object_or_404(ReportSnapshot, pk=pk)
    return render(request, 'reports/snapshot_detail.html', {'snapshot': snap})


def snapshot_lock(request, pk):
    snap = get_object_or_404(ReportSnapshot, pk=pk)
    if request.method == 'POST' and not snap.is_locked:
        snap.lock(locked_by=request.POST.get('locked_by', 'Admin'))
        messages.success(request, f'Snapshot locked and sealed.')
    return redirect('reports:snapshot_detail', pk=pk)


def generate_snapshot(request):
    """Generate and optionally lock a report snapshot for a period."""
    if request.method != 'POST':
        return redirect('reports:snapshot_list')

    from datetime import date
    report_code = request.POST.get('report_code', 'D1')
    start_str = request.POST.get('period_start')
    end_str = request.POST.get('period_end')

    try:
        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid period dates.')
        return redirect('reports:snapshot_list')

    # Generate data based on report type
    data = {}
    if report_code in ('D1', 'F1'):
        from reports.services.accounting import AccountingService
        from reports.services.expenses import ExpenseService
        acct = AccountingService(start, end)
        exp = ExpenseService(start, end)
        data = acct.to_income_statement()
        data['total_expenses'] = float(exp.total())
        data['net_profit'] = float(data.get('gross_profit', 0)) - float(exp.total())
        # Convert Decimals for JSON
        data = {k: float(v) if hasattr(v, 'is_integer') else
                   {ek: float(ev) for ek, ev in v.items()} if isinstance(v, dict) else str(v)
                for k, v in data.items()}
    elif report_code in ('D2', 'F2'):
        from reports.services.balance_sheet import BalanceSheetService
        svc = BalanceSheetService(end)
        data = {k: float(v) if hasattr(v, 'is_integer') else str(v)
                for k, v in svc.build().items()}

    snap, created = ReportSnapshot.objects.get_or_create(
        report_code=report_code,
        period_start=start,
        period_end=end,
        defaults={'data': data, 'generated_by': 'Admin'},
    )
    if not created:
        if snap.is_locked:
            messages.warning(request, 'A locked snapshot already exists for this period.')
            return redirect('reports:snapshot_detail', pk=snap.pk)
        snap.data = data
        snap.save(update_fields=['data'])

    if request.POST.get('lock'):
        snap.lock(locked_by='Admin')
        messages.success(request, f'Snapshot generated and locked for {start} → {end}.')
    else:
        messages.success(request, f'Snapshot saved for {start} → {end}.')

    return redirect('reports:snapshot_detail', pk=snap.pk)
