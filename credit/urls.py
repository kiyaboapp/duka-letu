from django.urls import path
from . import views

app_name = 'credit'

urlpatterns = [
    path('', views.DebtorListView.as_view(), name='index'),
    path('debtor/create/', views.DebtorCreateView.as_view(), name='debtor_create'),
    path('debtor/<int:pk>/', views.DebtorDetailView.as_view(), name='debtor_detail'),
    path('debt/create/', views.DebtCreateView.as_view(), name='debt_create'),
    path('repayment/create/', views.DebtReturnCreateView.as_view(), name='repayment_create'),
]
