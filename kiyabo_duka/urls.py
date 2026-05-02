"""
URL configuration for kiyabo_duka project.
"""
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Kiyabo Duka'
admin.site.site_title = 'Upendo Stationery'
admin.site.index_title = 'Shop Management'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')),
    path('catalog/', include('catalog.urls', namespace='catalog')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('sales/', include('sales.urls', namespace='sales')),
    path('credit/', include('credit.urls', namespace='credit')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('assets/', include('assets.urls', namespace='assets')),
    path('reports/', include('reports.urls', namespace='reports')),
]
