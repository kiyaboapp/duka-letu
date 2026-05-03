from django.shortcuts import render, get_object_or_404
from reports.models import ReportSnapshot


def snapshot_list(request):
    snapshots = ReportSnapshot.objects.order_by('-period_end')
    return render(request, 'reports/snapshot_list.html', {'snapshots': snapshots})


def snapshot_detail(request, pk):
    snap = get_object_or_404(ReportSnapshot, pk=pk)
    return render(request, 'reports/snapshot_detail.html', {'snapshot': snap})
