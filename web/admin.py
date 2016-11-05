from django.contrib import admin

from web.models import Customer, Element, Estimation, EstimationDetail


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    ordering = ('name',)
    search_fields = ('name', 'email')

admin.site.register(Customer, CustomerAdmin)


class ElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    ordering = ('name', )
    search_fields = ('name', )

admin.site.register(Element, ElementAdmin)


class EstimationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total_hours', 'total_value')
    ordering = ('customer', )
    search_fields = ('customer__name', )

admin.site.register(Estimation, EstimationAdmin)


class EstimationDetailAdmin(admin.ModelAdmin):
    list_display = ('estimation', 'element', 'service_type', 'hrs_total', 'val_total')
    ordering = ('estimation', 'element')
    search_fields = ('estimation__customer__name', 'element__name')

admin.site.register(EstimationDetail, EstimationDetailAdmin)
