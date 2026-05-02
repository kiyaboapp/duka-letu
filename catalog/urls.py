from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.ProductSpecListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductSpecDetailView.as_view(), name='product_detail'),
    path('api/product-specs/', views.product_spec_search, name='product_spec_search'),
]
