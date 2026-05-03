from decimal import Decimal
from reports.views.base import BaseReportView
from finance.models import BudgetLine
from reports.services.accounting import AccountingService
from reports.services.expenses import ExpenseService


class BudgetVsActualView(BaseReportView):
    template_name = 'reports/budget_vs_actual.html'

    def get_context(self, request, period):
        acct = AccountingService(period.start, period.end)
        exp = ExpenseService(period.start, period.end)

        actual_revenue = acct.net_sales()
        actual_cogs = acct.cogs()
        actual_expenses = exp.total()

        budgets = BudgetLine.objects.filter(
            financial_year=period.start.year,
            month__gte=period.start.month,
            month__lte=period.end.month,
        ).select_related('expense_type')

        budget_revenue = sum(b.budgeted_amount for b in budgets if b.budget_type == 'REVENUE')
        budget_cogs = sum(b.budgeted_amount for b in budgets if b.budget_type == 'COGS')
        budget_expenses = sum(b.budgeted_amount for b in budgets if b.budget_type == 'EXPENSE')

        def var(actual, budget):
            return actual - budget if budget else Decimal('0')

        return {
            'rows': [
                {'label': 'Net Sales Revenue', 'budget': budget_revenue, 'actual': actual_revenue, 'variance': var(actual_revenue, budget_revenue)},
                {'label': 'Cost of Goods Sold', 'budget': budget_cogs, 'actual': actual_cogs, 'variance': var(actual_cogs, budget_cogs)},
                {'label': 'Gross Profit', 'budget': budget_revenue - budget_cogs, 'actual': actual_revenue - actual_cogs, 'variance': var(actual_revenue - actual_cogs, budget_revenue - budget_cogs)},
                {'label': 'Operating Expenses', 'budget': budget_expenses, 'actual': actual_expenses, 'variance': var(actual_expenses, budget_expenses)},
                {'label': 'Net Profit', 'budget': budget_revenue - budget_cogs - budget_expenses, 'actual': actual_revenue - actual_cogs - actual_expenses, 'variance': var(actual_revenue - actual_cogs - actual_expenses, budget_revenue - budget_cogs - budget_expenses)},
            ],
            'budget_lines': budgets,
        }
