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

from viajes.views import (
    inicio,
    crear_viaje,
    cambiar_estado,
    finalizar_viaje,
    comprobante,
    archivar_viaje,
    archivados,
    restaurar_viaje,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio),
    path('crear/', crear_viaje),
    path('estado/<int:id>/', cambiar_estado),
    path('finalizar/<int:id>/', finalizar_viaje),
    path('comprobante/<int:id>/', comprobante),
    path('archivar/<int:id>/', archivar_viaje),
    path('archivados/', archivados),
    path('restaurar/<int:id>/', restaurar_viaje),
]