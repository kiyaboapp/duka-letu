from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.asset_create, name='asset_create'),
    path('<int:pk>/', views.asset_detail, name='asset_detail'),
    path('<int:pk>/edit/', views.asset_update, name='asset_update'),
    path('<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    path('<int:pk>/disposal/', views.asset_disposal, name='asset_disposal'),
]
