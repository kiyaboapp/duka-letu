from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.PurchaseListView.as_view(), name='index'),
    path('purchase/create/', views.PurchaseCreateView.as_view(), name='purchase_create'),
]
