from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('sale/create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('return/create/', views.ReturnInwardCreateView.as_view(), name='return_create'),
]
