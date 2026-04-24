from django.shortcuts import render, redirect, get_object_or_404
from .models import Viaje, Cliente, Chofer, Camioneta
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
import os


def cargar_camionetas_base():
    camionetas = [
        ("Fiat Fiorino", "chica"),
        ("Renault Kangoo", "chica"),
        ("Peugeot Partner", "chica"),
        ("Citroën Berlingo", "chica"),
        ("Volkswagen Saveiro", "chica"),
        ("Fiat Ducato", "grande"),
        ("Mercedes-Benz Sprinter", "grande"),
        ("Renault Master", "grande"),
        ("Iveco Daily", "grande"),
        ("Ford Transit", "grande"),
    ]

    for nombre, tamanio in camionetas:
        Camioneta.objects.get_or_create(
            nombre=nombre,
            defaults={"tamanio": tamanio, "valor_hora": 0}
        )


def inicio(request):
    cargar_camionetas_base()

    fecha = request.GET.get("fecha")

    if fecha:
        viajes = Viaje.objects.filter(fecha=fecha, activo=True).order_by("-hora")
    else:
        viajes = Viaje.objects.filter(activo=True).order_by("-fecha", "-hora")

    pendientes = viajes.filter(estado="pendiente")
    en_curso = viajes.filter(estado="en_curso")
    terminados = viajes.filter(estado="terminado")

    total = terminados.aggregate(Sum("precio_total"))["precio_total__sum"] or 0

    return render(request, "inicio.html", {
        "pendientes": pendientes,
        "en_curso": en_curso,
        "terminados": terminados,
        "total": total,
        "fecha_seleccionada": fecha
    })


def crear_viaje(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        origen = request.POST.get("origen", "").strip()
        destino = request.POST.get("destino", "").strip()
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        observaciones = request.POST.get("observaciones", "").strip()

        if telefono and not telefono.isdigit():
            return HttpResponse("Error: el teléfono solo debe contener números")

        cliente, _ = Cliente.objects.get_or_create(
            nombre=nombre,
            telefono=telefono
        )

        Viaje.objects.create(
            cliente=cliente,
            origen=origen,
            destino=destino,
            fecha=fecha,
            hora=hora if hora else None,
            observaciones=observaciones
        )

        return redirect("/")

    return render(request, "crear.html")


def cambiar_estado(request, id):
    viaje = get_object_or_404(Viaje, id=id)

    if viaje.estado == "pendiente":
        viaje.estado = "en_curso"
        viaje.save()
        return redirect("/")

    if viaje.estado == "en_curso":
        return redirect(f"/finalizar/{viaje.id}/")

    return redirect("/")


def finalizar_viaje(request, id):
    cargar_camionetas_base()

    viaje = get_object_or_404(Viaje, id=id)
    choferes = Chofer.objects.filter(activo=True)
    error = None

    if request.method == "POST":
        chofer_id = request.POST.get("chofer")
        horas = request.POST.get("horas")
        minutos = request.POST.get("minutos")

        if not chofer_id:
            error = "Tenés que seleccionar un chofer."
        else:
            try:
                horas = int(horas)
                minutos = int(minutos)
            except:
                error = "Horas y minutos deben ser números."

        if not error:
            chofer = get_object_or_404(Chofer, id=chofer_id)

            if not chofer.camioneta:
                error = "Este chofer no tiene camioneta asignada."
            elif chofer.camioneta.valor_hora == 0:
                error = "La camioneta no tiene precio por hora cargado."
            else:
                camioneta = chofer.camioneta
                tiempo_total = horas + (minutos / 60)
                total = tiempo_total * float(camioneta.valor_hora)

                viaje.chofer = chofer
                viaje.camioneta = camioneta
                viaje.horas_trabajadas = horas
                viaje.minutos_trabajados = minutos
                viaje.precio_total = total
                viaje.estado = "terminado"
                viaje.save()

                return redirect("/")

    return render(request, "finalizar.html", {
        "viaje": viaje,
        "choferes": choferes,
        "error": error
    })


def archivar_viaje(request, id):
    viaje = get_object_or_404(Viaje, id=id)
    viaje.activo = False
    viaje.save()
    return redirect("/")


def archivados(request):
    viajes = Viaje.objects.filter(activo=False).order_by("-fecha", "-hora")
    return render(request, "archivados.html", {"viajes": viajes})


def restaurar_viaje(request, id):
    viaje = get_object_or_404(Viaje, id=id)
    viaje.activo = True
    viaje.save()
    return redirect("/archivados/")


def comprobante(request, id):
    viaje = get_object_or_404(Viaje, id=id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="comprobante_{viaje.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    ancho, alto = A4

    logo_path = "C:/www/fletera/logo.png"

    if os.path.exists(logo_path):
        p.drawImage(
            logo_path,
            45,
            alto - 115,
            width=500,
            height=85,
            preserveAspectRatio=True,
            mask="auto"
        )

    p.setStrokeColor(colors.lightgrey)
    p.roundRect(40, 90, ancho - 80, alto - 220, 10, stroke=True, fill=False)

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, alto - 150, f"Comprobante N° {viaje.id}")

    p.setFont("Helvetica", 10)
    p.drawString(50, alto - 170, f"Fecha viaje: {viaje.fecha}")
    p.drawString(250, alto - 170, f"Hora: {viaje.hora if viaje.hora else '-'}")
    p.drawString(50, alto - 185, f"Emitido: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    p.line(50, alto - 200, ancho - 50, alto - 200)

    y = alto - 230

    def fila(label, valor):
        nonlocal y
        p.setFont("Helvetica-Bold", 11)
        p.drawString(60, y, label)
        p.setFont("Helvetica", 11)
        p.drawString(190, y, str(valor) if valor else "-")
        y -= 25

    fila("Cliente:", viaje.cliente.nombre)
    fila("Teléfono:", viaje.cliente.telefono)
    fila("Origen:", viaje.origen)
    fila("Destino:", viaje.destino)
    fila("Estado:", viaje.estado)

    if viaje.chofer:
        fila("Chofer:", viaje.chofer)

    if viaje.camioneta:
        fila("Vehículo:", viaje.camioneta.nombre)
        fila("Valor hora:", f"$ {int(viaje.camioneta.valor_hora):,}".replace(",", "."))

    if viaje.horas_trabajadas is not None:
        fila("Tiempo:", f"{viaje.horas_trabajadas} hs {viaje.minutos_trabajados} min")

    total = int(viaje.precio_total) if viaje.precio_total else 0

    p.setFillColor(colors.HexColor("#d1e7dd"))
    p.roundRect(50, y - 40, ancho - 100, 45, 8, fill=True, stroke=False)

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(60, y - 15, f"TOTAL: $ {total:,}".replace(",", "."))

    y -= 80
    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, y, "Firma:")
    p.line(120, y, 300, y)

    p.setFillColor(colors.grey)
    p.setFont("Helvetica", 9)
    p.drawString(50, 70, "Comprobante generado automáticamente")
    p.drawString(50, 55, "Gracias por confiar en MasterFlet")

    p.showPage()
    p.save()

    return response