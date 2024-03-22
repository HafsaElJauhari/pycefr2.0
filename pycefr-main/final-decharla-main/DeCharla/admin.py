from django.contrib import admin
from .models import Sesion, Contrasena, Sala, Mensaje, Configuracion, UltimaVisita, Voto

# Register your models here.
admin.site.register(Sesion)
admin.site.register(Contrasena)
admin.site.register(Sala)
admin.site.register(Mensaje)
admin.site.register(Configuracion)
admin.site.register(UltimaVisita)
admin.site.register(Voto)