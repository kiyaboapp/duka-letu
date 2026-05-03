from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('sale/create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('sale/create/partial/', views.sale_create_partial, name='sale_create_partial'),
    path('sale/<int:pk>/return/', views.sale_return_partial, name='sale_return'),
    path('return/create/', views.ReturnInwardCreateView.as_view(), name='return_create'),
]
