from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.ProductSpecListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductSpecDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/sell/', views.product_sell_partial, name='product_sell'),
    path('products/<int:pk>/purchase/', views.product_purchase_partial, name='product_purchase'),
    path('products/<int:pk>/credit-sale/', views.product_credit_sale_partial, name='product_credit_sale'),
    path('api/product-specs/', views.product_spec_search, name='product_spec_search'),
]
