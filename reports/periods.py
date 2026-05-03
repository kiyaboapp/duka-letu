"""
reports/periods.py — ReportPeriod engine.
Single source of truth for all date range logic across every report.
"""
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Optional
import calendar

PRESET_CHOICES = [
    ('today', 'Today'),
    ('yesterday', 'Yesterday'),
    ('this_week', 'This Week'),
    ('last_week', 'Last Week'),
    ('this_month', 'This Month'),
    ('last_month', 'Last Month'),
    ('this_quarter', 'This Quarter'),
    ('last_quarter', 'Last Quarter'),
    ('this_year', 'This Year'),
    ('last_year', 'Last Year'),
    ('custom', 'Custom Range'),
]

_PRESET_CODES = {k for k, _ in PRESET_CHOICES}


@dataclass
class ReportPeriod:
    start: date
    end: date
    preset: str
    label: str

    @classmethod
    def resolve(cls, preset=None, start=None, end=None,
                default_preset='this_month', reference=None):
        today = reference or date.today()
        if preset == 'custom' and start and end:
            if start > end:
                start, end = end, start
            return cls(start=start, end=end, preset='custom', label=f'{start} → {end}')
        code = preset if preset in _PRESET_CODES else default_preset
        s, e, label = cls._compute(code, today)
        return cls(start=s, end=e, preset=code, label=label)

    @staticmethod
    def _compute(code, today):
        if code == 'today':
            return today, today, f'Today ({today:%d %b %Y})'
        if code == 'yesterday':
            y = today - timedelta(days=1)
            return y, y, f'Yesterday ({y:%d %b %Y})'
        if code == 'this_week':
            mon = today - timedelta(days=today.weekday())
            sun = mon + timedelta(days=6)
            return mon, sun, f'This Week ({mon:%d %b} – {sun:%d %b %Y})'
        if code == 'last_week':
            mon = today - timedelta(days=today.weekday() + 7)
            sun = mon + timedelta(days=6)
            return mon, sun, f'Last Week ({mon:%d %b} – {sun:%d %b %Y})'
        if code == 'this_month':
            s = today.replace(day=1)
            e = today.replace(day=calendar.monthrange(today.year, today.month)[1])
            return s, e, f'{today:%B %Y}'
        if code == 'last_month':
            last = today.replace(day=1) - timedelta(days=1)
            return last.replace(day=1), last, f'{last:%B %Y}'
        if code == 'this_quarter':
            q = (today.month - 1) // 3
            sm = q * 3 + 1
            em = sm + 2
            s = date(today.year, sm, 1)
            e = date(today.year, em, calendar.monthrange(today.year, em)[1])
            return s, e, f'Q{q+1} {today.year}'
        if code == 'last_quarter':
            q = (today.month - 1) // 3
            lq = q - 1 if q > 0 else 3
            yr = today.year if q > 0 else today.year - 1
            sm = lq * 3 + 1
            em = sm + 2
            s = date(yr, sm, 1)
            e = date(yr, em, calendar.monthrange(yr, em)[1])
            return s, e, f'Q{lq+1} {yr}'
        if code == 'this_year':
            return date(today.year, 1, 1), date(today.year, 12, 31), f'Year {today.year}'
        if code == 'last_year':
            y = today.year - 1
            return date(y, 1, 1), date(y, 12, 31), f'Year {y}'
        # fallback
        s = today.replace(day=1)
        e = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        return s, e, f'{today:%B %Y}'

    @property
    def days(self):
        return (self.end - self.start).days + 1

    @property
    def is_single_day(self):
        return self.start == self.end

    def __str__(self):
        return self.label
