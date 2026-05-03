from django.db import models
from django.utils import timezone


class ReportSnapshot(models.Model):
    REPORT_CODES = [
        ('D1', 'Monthly Income Statement'),
        ('D2', 'Monthly Balance Sheet'),
        ('D3', 'Monthly Cash Flow'),
        ('D4', 'Monthly Expense Analysis'),
        ('D5', 'Monthly Debtor Aging'),
        ('D6', 'Monthly Liability Schedule'),
        ('D7', 'Monthly Drawings Summary'),
        ('E1', 'Quarterly Management Accounts'),
        ('E2', 'Quarterly Stock Valuation'),
        ('F1', 'Annual Income Statement'),
        ('F2', 'Annual Balance Sheet'),
        ('F5', 'Annual Budget vs Actual'),
    ]

    report_code = models.CharField(max_length=10, choices=REPORT_CODES)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_by = models.CharField(max_length=255, default='System')
    generated_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)
    locked_by = models.CharField(max_length=255, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    data = models.JSONField()
    checksum = models.CharField(max_length=64, blank=True)

    class Meta:
        unique_together = [['report_code', 'period_start', 'period_end']]
        ordering = ['-period_end', 'report_code']

    def __str__(self):
        status = '🔒' if self.is_locked else '📄'
        return f"{status} {self.get_report_code_display()} ({self.period_start} → {self.period_end})"

    def lock(self, locked_by: str) -> None:
        import hashlib, json
        self.is_locked = True
        self.locked_by = locked_by
        self.locked_at = timezone.now()
        self.checksum = hashlib.sha256(
            json.dumps(self.data, sort_keys=True, default=str).encode()
        ).hexdigest()
        self.save(update_fields=['is_locked', 'locked_by', 'locked_at', 'checksum'])
