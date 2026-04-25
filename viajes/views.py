from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Viaje, Cliente, Chofer, Camioneta
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from decimal import Decimal


# 🔥 INICIO
def inicio(request):
    viajes = Viaje.objects.filter(activo=True)

    total_viajes = viajes.count()
    pendientes = viajes.filter(estado='pendiente')
    en_curso = viajes.filter(estado='en_curso')
    terminados = viajes.filter(estado='terminado')

    total_ganado = terminados.aggregate(
        total=Sum('precio_total')
    )['total'] or 0

    viajes_recientes = viajes.order_by('-fecha', '-hora')[:5]

    return render(request, 'inicio.html', {
        'viajes_recientes': viajes_recientes,
        'total_viajes': total_viajes,
        'pendientes': pendientes,
        'en_curso': en_curso,
        'terminados': terminados,
        'total_ganado': total_ganado,
    })


# 🔥 TODOS LOS VIAJES
def todos_los_viajes(request):
    viajes = Viaje.objects.filter(activo=True).order_by('-fecha', '-hora')

    return render(request, 'todos_los_viajes.html', {
        'viajes': viajes
    })


# 🔥 REPORTES
def reportes(request):
    viajes = Viaje.objects.filter(activo=True)

    total_ganado = viajes.filter(
        estado='terminado'
    ).aggregate(Sum('precio_total'))['precio_total__sum'] or 0

    return render(request, 'reportes.html', {
        'total_ganado': total_ganado,
        'total_viajes': viajes.count(),
        'terminados': viajes.filter(estado='terminado').count(),
        'pendientes': viajes.filter(estado='pendiente').count(),
        'en_curso': viajes.filter(estado='en_curso').count(),
    })


# 🔥 CREAR VIAJE
def crear_viaje(request):
    clientes = Cliente.objects.all()
    choferes = Chofer.objects.filter(activo=True)
    camionetas = Camioneta.objects.all()

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        chofer_id = request.POST.get('chofer')
        camioneta_id = request.POST.get('camioneta')

        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        observaciones = request.POST.get('observaciones')

        Viaje.objects.create(
            cliente_id=cliente_id,
            chofer_id=chofer_id,
            camioneta_id=camioneta_id,
            origen=origen,
            destino=destino,
            fecha=fecha,
            hora=hora,
            observaciones=observaciones,
            estado='pendiente',
            activo=True
        )

        return redirect('/')

    return render(request, 'crear_viaje.html', {
        'clientes': clientes,
        'choferes': choferes,
        'camionetas': camionetas,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })


# 🔥 CAMBIAR ESTADO
def cambiar_estado(request, id):
    viaje = get_object_or_404(Viaje, id=id)

    if viaje.estado == 'pendiente':
        viaje.estado = 'en_curso'
        viaje.save()
        return redirect('/')

    elif viaje.estado == 'en_curso':
        return redirect('finalizar_viaje', id=viaje.id)

    return redirect('/')


# 🔥 FINALIZAR VIAJE
def finalizar_viaje(request, id):
    viaje = get_object_or_404(Viaje, id=id)
    choferes = Chofer.objects.filter(activo=True)

    if request.method == 'POST':
        chofer_id = request.POST.get('chofer')
        horas = int(request.POST.get('horas') or 0)
        minutos = int(request.POST.get('minutos') or 0)

        if not chofer_id:
            return render(request, 'finalizar_viaje.html', {
                'viaje': viaje,
                'choferes': choferes,
                'error': 'Tenés que seleccionar un chofer.'
            })

        if not viaje.camioneta:
            return render(request, 'finalizar_viaje.html', {
                'viaje': viaje,
                'choferes': choferes,
                'error': 'Este viaje no tiene camioneta asignada.'
            })

        if horas == 0 and minutos == 0:
            return render(request, 'finalizar_viaje.html', {
                'viaje': viaje,
                'choferes': choferes,
                'error': 'Tenés que cargar horas o minutos trabajados.'
            })

        chofer = get_object_or_404(Chofer, id=chofer_id)

        total_horas = Decimal(horas) + (Decimal(minutos) / Decimal(60))
        precio_total = total_horas * viaje.camioneta.valor_hora

        viaje.chofer = chofer
        viaje.horas_trabajadas = horas
        viaje.minutos_trabajados = minutos
        viaje.precio_total = precio_total
        viaje.estado = 'terminado'
        viaje.save()

        return redirect('/')

    return render(request, 'finalizar_viaje.html', {
        'viaje': viaje,
        'choferes': choferes,
    })


# 🔥 ARCHIVAR
def archivar_viaje(request, id):
    viaje = get_object_or_404(Viaje, id=id)
    viaje.activo = False
    viaje.save()
    return redirect('/')


# 🔥 ARCHIVADOS
def archivados(request):
    viajes = Viaje.objects.filter(activo=False)

    return render(request, 'archivados.html', {
        'viajes': viajes
    })


# 🔥 RESTAURAR
def restaurar_viaje(request, id):
    viaje = get_object_or_404(Viaje, id=id)
    viaje.activo = True
    viaje.save()
    return redirect('/archivados/')


# 🔥 PDF
def comprobante(request, id):
    viaje = get_object_or_404(Viaje, id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="viaje_{id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    p.drawString(100, 800, "Comprobante de Viaje")
    p.drawString(100, 750, f"Cliente: {viaje.cliente}")
    p.drawString(100, 730, f"Chofer: {viaje.chofer}")
    p.drawString(100, 710, f"Camioneta: {viaje.camioneta}")
    p.drawString(100, 690, f"Origen: {viaje.origen}")
    p.drawString(100, 670, f"Destino: {viaje.destino}")
    p.drawString(100, 650, f"Fecha: {viaje.fecha}")
    p.drawString(100, 630, f"Hora: {viaje.hora}")
    p.drawString(100, 610, f"Horas: {viaje.horas_trabajadas} hs {viaje.minutos_trabajados} min")
    p.drawString(100, 590, f"Precio: ${viaje.precio_total}")
    p.drawString(100, 570, f"Estado: {viaje.estado}")

    p.showPage()
    p.save()

    return response