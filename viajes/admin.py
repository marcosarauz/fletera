from django.contrib import admin
from .models import Cliente, Viaje, Chofer, Camioneta


admin.site.site_header = "MasterFlet"
admin.site.site_title = "MasterFlet Admin"
admin.site.index_title = "Panel de administración"


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'camioneta', 'activo')
    list_filter = ('activo', 'camioneta')
    search_fields = ('nombre', 'apellido', 'dni')


@admin.register(Camioneta)
class CamionetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tamanio', 'valor_hora')
    list_filter = ('tamanio',)
    search_fields = ('nombre',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono')
    search_fields = ('nombre', 'telefono')


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'origen', 'destino', 'fecha', 'estado', 'precio_total', 'activo')
    list_filter = ('estado', 'fecha', 'activo')
    search_fields = ('cliente__nombre', 'origen', 'destino')