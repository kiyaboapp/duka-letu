from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.PurchaseListView.as_view(), name='index'),
    path('purchase/create/', views.PurchaseCreateView.as_view(), name='purchase_create'),
    path('purchase/<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchase/<int:pk>/edit/', views.PurchaseUpdateView.as_view(), name='purchase_update'),
    path('purchase/<int:pk>/delete/', views.PurchaseDeleteView.as_view(), name='purchase_delete'),
    path('return/create/', views.ReturnOutwardCreateView.as_view(), name='return_outward_create'),
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
]
