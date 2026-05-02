from django.contrib import admin
from .models import Sale, ReturnInward, OfficeUseCategory, SaleOfficeUse, DrawingCategory, Drawing


admin.site.register(Sale)
admin.site.register(ReturnInward)
admin.site.register(OfficeUseCategory)
admin.site.register(SaleOfficeUse)
admin.site.register(DrawingCategory)
admin.site.register(Drawing)

# Register your models here.
