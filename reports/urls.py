from django.urls import path
from reports.views.index import index
from reports.views.income_statement import IncomeStatementView
from reports.views.stock_report import stock_report
from reports.views.debtor_aging import debtor_aging
from reports.views.daily_sales import DailySalesView
from reports.views.expense_analysis import ExpenseAnalysisView
from reports.views.balance_sheet import BalanceSheetView
from reports.views.cash_flow import CashFlowView
from reports.views.low_stock import low_stock
from reports.views.drawings_summary import DrawingsSummaryView
from reports.views.purchase_summary import PurchaseSummaryView
from reports.views.liability_schedule import liability_schedule
from reports.views.product_profitability import ProductProfitabilityView
from reports.views.budget_vs_actual import BudgetVsActualView
from reports.views.cash_reconciliation import CashReconciliationView
from reports.views.snapshots import snapshot_list, snapshot_detail, generate_snapshot, snapshot_lock

app_name = 'reports'

urlpatterns = [
    path('', index, name='index'),
    path('income-statement/', IncomeStatementView.as_view(), name='income_statement'),
    path('stock-report/', stock_report, name='stock_report'),
    path('debtor-aging/', debtor_aging, name='debtor_aging'),
    path('daily-sales/', DailySalesView.as_view(), name='daily_sales'),
    path('expense-analysis/', ExpenseAnalysisView.as_view(), name='expense_analysis'),
    path('balance-sheet/', BalanceSheetView.as_view(), name='balance_sheet'),
    path('cash-flow/', CashFlowView.as_view(), name='cash_flow'),
    path('low-stock/', low_stock, name='low_stock'),
    path('drawings/', DrawingsSummaryView.as_view(), name='drawings_summary'),
    path('purchases/', PurchaseSummaryView.as_view(), name='purchase_summary'),
    path('liabilities/', liability_schedule, name='liability_schedule'),
    path('product-profitability/', ProductProfitabilityView.as_view(), name='product_profitability'),
    path('budget-vs-actual/', BudgetVsActualView.as_view(), name='budget_vs_actual'),
    path('cash-reconciliation/', CashReconciliationView.as_view(), name='cash_reconciliation'),
    path('snapshots/', snapshot_list, name='snapshot_list'),
    path('snapshots/generate/', generate_snapshot, name='generate_snapshot'),
    path('snapshots/<int:pk>/', snapshot_detail, name='snapshot_detail'),
    path('snapshots/<int:pk>/lock/', snapshot_lock, name='snapshot_lock'),
]
