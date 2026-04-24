from django.contrib import admin
from .models import Cliente, Viaje, Chofer, Camioneta


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'camioneta', 'activo')
    fields = ('nombre', 'apellido', 'dni', 'camioneta', 'activo')


@admin.register(Camioneta)
class CamionetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tamanio', 'valor_hora')


admin.site.register(Cliente)
admin.site.register(Viaje)