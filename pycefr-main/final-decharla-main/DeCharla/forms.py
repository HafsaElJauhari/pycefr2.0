from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Mensaje, Configuracion

class MensajeForm(forms.ModelForm):
    contenido = forms.CharField(widget=forms.Textarea, label=_('Contenido:'))
    es_url = forms.BooleanField(required=False, label=_('Seleccionar si el mensaje es una url:'))
    class Meta:
        model = Mensaje
        fields = ['contenido', 'es_url']

class ConfiguracionForm(forms.Form):
    nombre = forms.CharField(label=_('Nombre'), max_length=100)
    tamano_fuente = forms.ChoiceField(label=_('Tamaño de Fuente'), choices=Configuracion.TAMANO_FUENTE_CHOICES)
    tipo_fuente = forms.ChoiceField(label=_('Tipo de Fuente'), choices=Configuracion.TIPO_FUENTE_CHOICES)

class SalaForm(forms.Form):
    nombre_sala = forms.CharField(label=_('Nombre de la sala'), max_length=100)
