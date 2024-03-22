from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Contrasena(models.Model):
    contrasena = models.TextField()

    def __str__(self):
        return str(self.id) + ": " + self.contrasena

class Sesion(models.Model):
    cookie_user = models.CharField(max_length=32)

    def __str__(self):
        return self.cookie_user

class Sala(models.Model):
    creador = models.ForeignKey(Sesion, on_delete=models.CASCADE)
    nombre = models.TextField(max_length=50)
    fecha = models.DateTimeField('visitado')
    votos = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Voto(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE)
    megusta = models.BooleanField(default=False)

    def __str(self):
        return self.sala.nombre + ": " + self.sesion.cookie_user

class UltimaVisita(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE )
    last_visit = models.DateTimeField(auto_now=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    mensajes_no_leidos = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.sala) + '-->' +  str(self.last_visit)

class Mensaje(models.Model):
    creador = models.CharField(max_length=100)
    contenido = models.TextField()
    fecha = models.DateTimeField('publicado', auto_now_add=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    es_url = models.BooleanField(default=False)

    def __str__(self):
        return self.contenido


class Configuracion(models.Model):
    sesion = models.OneToOneField(Sesion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    TAMANO_FUENTE_CHOICES = [
        (12, _('Pequeño')),
        (16, _('Mediano')),
        (20, _('Grande')),
    ]
    tamano_fuente = models.PositiveIntegerField(choices=TAMANO_FUENTE_CHOICES, default=12)
    TIPO_FUENTE_CHOICES = [
        ('Arial', 'Arial'),
        ('Times New Roman', 'Times New Roman'),
        ('Verdana', 'Verdana'),
    ]
    tipo_fuente = models.CharField(max_length=50, choices=TIPO_FUENTE_CHOICES, default='Arial')

    def __str__(self):
        return self.nombre
