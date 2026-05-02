from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.index, name='index'),
    path('income-statement/', views.IncomeStatementView.as_view(), name='income_statement'),
    path('stock-report/', views.StockReportView.as_view(), name='stock_report'),
    path('debtor-aging/', views.DebtorAgingView.as_view(), name='debtor_aging'),
]
