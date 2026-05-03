from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.index, name='index'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/new/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/update/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/toggle/', views.expense_toggle, name='expense_toggle'),
    path('obligation/<int:pk>/pay/', views.obligation_pay, name='obligation_pay'),
    path('liabilities/', views.liability_list, name='liability_list'),
    path('liabilities/<int:pk>/', views.liability_detail, name='liability_detail'),
    path('liabilities/<int:pk>/pay/', views.liability_pay, name='liability_pay'),
]
