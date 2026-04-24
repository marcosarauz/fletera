from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.nombre


class Camioneta(models.Model):
    TAMANIOS = [
        ('chica', 'Chica'),
        ('grande', 'Grande'),
    ]

    nombre = models.CharField(max_length=100)
    tamanio = models.CharField(max_length=20, choices=TAMANIOS)
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} - {self.tamanio} - ${self.valor_hora}/hora"


class Chofer(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    dni = models.CharField(max_length=20, blank=True)
    camioneta = models.ForeignKey(Camioneta, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Viaje(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('terminado', 'Terminado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    origen = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    fecha = models.DateField()
    hora = models.TimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    chofer = models.ForeignKey(Chofer, on_delete=models.SET_NULL, null=True, blank=True)
    camioneta = models.ForeignKey(Camioneta, on_delete=models.SET_NULL, null=True, blank=True)

    horas_trabajadas = models.PositiveIntegerField(null=True, blank=True)
    minutos_trabajados = models.PositiveIntegerField(null=True, blank=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.cliente} - {self.origen} a {self.destino}"