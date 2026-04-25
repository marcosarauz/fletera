"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import logout
from django.shortcuts import redirect

from viajes.views import (
    inicio,
    crear_viaje,
    cambiar_estado,
    finalizar_viaje,
    comprobante,
    archivar_viaje,
    archivados,
    restaurar_viaje,
    todos_los_viajes,
    reportes,
)

# 🔴 LOGOUT
def cerrar_sesion(request):
    logout(request)
    return redirect('/')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', inicio, name='inicio'),
    path('viajes/', todos_los_viajes, name='viajes'),
    path('reportes/', reportes, name='reportes'),

    path('crear/', crear_viaje, name='crear_viaje'),
    path('estado/<int:id>/', cambiar_estado, name='cambiar_estado'),
    path('finalizar/<int:id>/', finalizar_viaje, name='finalizar_viaje'),
    path('comprobante/<int:id>/', comprobante, name='comprobante'),
    path('archivar/<int:id>/', archivar_viaje, name='archivar_viaje'),
    path('archivados/', archivados, name='archivados'),
    path('restaurar/<int:id>/', restaurar_viaje, name='restaurar_viaje'),

    path('logout/', cerrar_sesion, name='logout'),
]