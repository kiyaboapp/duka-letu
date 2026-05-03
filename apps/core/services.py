"""
Core utilities for Kiyabo Duka.
Shared mixins, decorators, and helper functions.
Provides context-aware actions, URL generation, and business logic encapsulation.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class ActionMixin:
    """
    Mixin to make models self-aware of their actions and URLs.
    Enables templates to be context-driven: {{ object.get_action_url('edit') }}
    """
    
    # Override in specific models if URL patterns differ from convention
    ACTION_URL_NAMES = {}

    def get_action_url(self, action: str, **kwargs) -> str:
        """
        Dynamically generate URL for an action.
        Usage: instance.get_action_url('edit') or instance.get_sell_url()
        """
        app_label = self._meta.app_label
        model_name = self._meta.model_name
        
        # Check for model-specific override
        url_pattern = self.ACTION_URL_NAMES.get(action)
        
        if not url_pattern:
            # Use conventional pattern
            action_map = {
                'view': f'{app_label}:{model_name}_detail',
                'edit': f'{app_label}:{model_name}_update',
                'delete': f'{app_label}:{model_name}_delete',
                'duplicate': f'{app_label}:{model_name}_duplicate',
                'list': f'{app_label}:{model_name}_list',
                'create': f'{app_label}:{model_name}_create',
            }
            url_pattern = action_map.get(action)
        
        if not url_pattern:
            return '#'
        
        try:
            if action in ['list', 'create']:
                return reverse(url_pattern)
            return reverse(url_pattern, kwargs={'pk': self.pk}, **kwargs)
        except Exception:
            return "#"

    def get_available_actions(self, user=None) -> list:
        """
        Returns list of available actions for this instance.
        Override in models to add business rules (e.g., can't delete posted sales).
        """
        actions = ['view']
        if self.can_edit(user):
            actions.append('edit')
        if self.can_delete(user):
            actions.append('delete')
        if hasattr(self, 'can_duplicate') and self.can_duplicate():
            actions.append('duplicate')
        return actions

    def can_edit(self, user=None) -> bool:
        """Default: True if object exists. Override for specific logic."""
        return bool(self.pk)

    def can_delete(self, user=None) -> bool:
        """Default: True. Override to prevent deleting critical records."""
        return True

    def get_status_badge(self) -> dict:
        """
        Returns status info for UI badges.
        Returns: {'label': str, 'color': str (tailwind class)}
        Override in models for custom status logic.
        """
        return {'label': 'Active', 'color': 'bg-green-100 text-green-800'}

    def get_action_buttons_html(self, request=None, extra_classes: str = "") -> str:
        """
        Return HTML snippet of action buttons for this instance.
        Useful for rendering in admin, API responses, or partials.
        """
        buttons = []
        actions = self.get_available_actions(request.user if request else None)
        
        icon_map = {
            'view': '👁️',
            'edit': '✏️',
            'delete': '🗑️',
            'duplicate': '📋'
        }
        
        for action in actions:
            url = self.get_action_url(action)
            label = action.capitalize()
            icon = icon_map.get(action, '')
            
            color_class = {
                'view': 'bg-blue-50 text-blue-600 hover:bg-blue-100',
                'edit': 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100',
                'delete': 'bg-red-50 text-red-600 hover:bg-red-100',
                'duplicate': 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            }.get(action, 'bg-gray-50 text-gray-600')
            
            buttons.append(
                f'<a href="{url}" class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium transition-colors {color_class} {extra_classes}">'
                f'{icon} <span class="ml-1">{label}</span></a>'
            )
        
        return ' '.join(buttons)


class ReportEnricher:
    """
    Enhances report data with trends, variances, and actionable insights.
    Makes reports self-explanatory and decision-ready.
    """
    
    @staticmethod
    def calculate_trend(current: float, previous: float) -> dict:
        """Calculates percentage change and direction."""
        if previous == 0:
            return {'value': 0, 'direction': 'neutral', 'label': 'New', 'percentage': 0}
        
        change = ((current - previous) / abs(previous)) * 100
        direction = 'up' if change > 0 else ('down' if change < 0 else 'neutral')
        
        return {
            'value': round(abs(change), 1),
            'direction': direction,
            'label': f"+{change:.1f}%" if change > 0 else f"{change:.1f}%",
            'percentage': change
        }

    @staticmethod
    def format_currency(amount: float, currency: str = "TZS") -> str:
        """Formats amount with thousands separators."""
        return f"{currency} {amount:,.0f}"

    @staticmethod
    def format_number(num: float, decimals: int = 0) -> str:
        """Formats number with thousands separators."""
        if decimals == 0:
            return f"{num:,.0f}"
        return f"{num:,.{decimals}f}"

    @staticmethod
    def get_insight(data: dict, context: str = "") -> list:
        """
        Generates natural language insights from report data.
        Returns list of actionable recommendations.
        """
        insights = []
        
        # Profitability insights
        gross_margin = data.get('gross_profit_margin', 0)
        if gross_margin < 15:
            insights.append("⚠️ Profit margins are below target (15%). Consider reviewing pricing strategy or negotiating better supplier rates.")
        elif gross_margin > 40:
            insights.append("✅ Excellent profit margins! Consider reinvesting in inventory expansion.")
        
        # Inventory insights
        stock_turnover = data.get('stock_turnover_days', 0)
        if stock_turnover > 60:
            insights.append("⚠️ Stock is moving slowly (>60 days). Consider promotions to clear aging inventory.")
        elif stock_turnover < 15:
            insights.append("📦 Fast-moving inventory! Ensure stock levels are adequate to meet demand.")
        
        # Debtor insights
        debtor_days = data.get('debtor_days', 0)
        if debtor_days > 30:
            insights.append(f"⚠️ Debtors are taking {debtor_days:.0f} days on average to pay. Follow up on aging accounts.")
        
        # Cash flow insights
        cash_ratio = data.get('cash_ratio', 0)
        if cash_ratio < 1.0:
            insights.append("⚠️ Low cash reserves relative to liabilities. Monitor cash flow closely.")
        
        # Budget variance
        budget_variance = data.get('budget_variance_percent', 0)
        if abs(budget_variance) > 10:
            direction = "over" if budget_variance > 0 else "under"
            insights.append(f"📊 Expenses are {abs(budget_variance):.1f}% {direction} budget. Review spending patterns.")
        
        if not insights:
            insights.append("✅ Operations look healthy. All key metrics within target ranges.")
        
        return insights


def json_response(data, status=200):
    """Quick JSON response helper."""
    return JsonResponse(data, status=status, safe=False)


def require_ajax(view_func):
    """Decorator to require AJAX requests."""
    from functools import wraps
    
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def handle_form_errors(form, request):
    """Add form errors to Django messages framework."""
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                field_label = form.fields[field].label if field in form.fields else field
                messages.error(request, f"{field_label}: {error}")
        return False
    return True


def parse_decimal(value, default=Decimal('0')):
    """Safely parse a value to Decimal."""
    if value is None or value == '':
        return default
    try:
        return Decimal(str(value))
    except:
        return default


def get_date_range_preset(preset: str):
    """
    Returns (start_date, end_date) for common date range presets.
    Usage: start, end = get_date_range_preset('this_month')
    """
    today = timezone.now().date()
    
    presets = {
        'today': (today, today),
        'yesterday': (today - timedelta(days=1), today - timedelta(days=1)),
        'this_week': (today - timedelta(days=today.weekday()), today),
        'last_week': (
            today - timedelta(days=today.weekday() + 7),
            today - timedelta(days=today.weekday() + 1)
        ),
        'this_month': (today.replace(day=1), today),
        'last_month': (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            (today.replace(day=1) - timedelta(days=1))
        ),
        'this_year': (today.replace(month=1, day=1), today),
        'last_year': (
            today.replace(year=today.year - 1, month=1, day=1),
            today.replace(year=today.year - 1, month=12, day=31)
        ),
    }
    
    return presets.get(preset, (today - timedelta(days=30), today))
