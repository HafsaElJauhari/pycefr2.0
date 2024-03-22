import secrets
from datetime import timedelta
from xml.dom import minidom
from django.utils import translation
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .forms import MensajeForm, ConfiguracionForm, SalaForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sala, Mensaje, Configuracion, Sesion, Contrasena, UltimaVisita, Voto


# Create your views here.

def configuracion_default(sesion):
    configuracion = Configuracion(sesion=sesion, nombre="Anónimo",
                                  tamano_fuente=12, tipo_fuente='Arial')
    configuracion.save()
    return configuracion

@csrf_exempt
def manejar_login(request):
    if request.method == 'POST':
        if not 'cookie_user' in request.COOKIES:
            contrasena = request.POST.get('contrasena')
            try:
                expiration = timezone.now() + timedelta(days=3650)
                Contrasena.objects.get(contrasena=contrasena)
                auth_token = secrets.token_hex(16)
                sesion = Sesion(cookie_user=auth_token)
                sesion.save()
                configuracion = configuracion_default(sesion)
                configuracion.save()
                response = HttpResponseRedirect('/DeCharla/')
                response.status_code = 301
                response.set_cookie('cookie_user', auth_token, expires=expiration)
                return response

            except Contrasena.DoesNotExist:
                return HttpResponse('Unauthorized', status=401)

        else:
            return HttpResponseRedirect('/DeCharla/')
    else:
        return render(request, 'registration/login.html')



def sala_dinamica(request, sala):
    if 'cookie_user' in request.COOKIES:
        cookie_user = request.COOKIES['cookie_user']
        configuracion = Configuracion.objects.get(sesion__cookie_user=cookie_user)
    else:
        return redirect('login')

    try:
        Sala.objects.get(nombre=sala)
        form = MensajeForm()
        total_mensajes_textuales, total_mensajes_imagenes, total_salas_activas = pie_pagina()
        template = loader.get_template('DeCharla/sala_dinamica.html')
        contexto = {
            'sala': sala,
            'form': form,
            'configuracion': configuracion,
            'total_mensajes_textuales': total_mensajes_textuales,
            'total_mensajes_imagenes': total_mensajes_imagenes,
            'total_salas_activas': total_salas_activas,
        }
        return HttpResponse(template.render(contexto, request))

    except Sala.DoesNotExist:
        raise Http404("Lo siento el nombre de recurso introducido para la sala no existe. Inténtelo de nuevo.")

def manejar_logout(request):
    logout(request)

    response = redirect('login')
    response.delete_cookie('cookie_user')

    return response

@csrf_exempt
def set_language(request):
    if request.method == 'POST' and 'language' in request.POST:
        language = request.POST['language']
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language

    return redirect(request.POST.get('next') or '/')

def sala_json(request, sala):
    sala = get_object_or_404(Sala, nombre=sala)
    mensajes = Mensaje.objects.filter(sala=sala)

    mensaje_list = []
    for mensaje in mensajes:
        mensaje_dict = {
            'author': mensaje.creador,
            'text': mensaje.contenido,
            'isimg': mensaje.es_url,
            'date': mensaje.fecha.strftime('%Y-%m-%d:%H:%M:%S')
        }
        mensaje_list.append(mensaje_dict)

    return JsonResponse(mensaje_list, safe=False)

@csrf_exempt
def crear_sala(request):
    form_sala = SalaForm(request.POST)
    if request.method == 'POST':
        if form_sala.is_valid():
            nombre_sala = form_sala.cleaned_data['nombre_sala']
            if Sala.objects.filter(nombre=nombre_sala).exists():
                return redirect('manejar_salas', sala=nombre_sala)

            fecha_actual = timezone.now()
            cookie_user = request.COOKIES['cookie_user']
            sesion = Sesion.objects.get(cookie_user=cookie_user)
            sala = Sala(nombre=nombre_sala, fecha=fecha_actual, creador=sesion)
            sala.save()
            sesiones = Sesion.objects.all()
            for sesion in sesiones:
                if not Voto.objects.filter(sesion=sesion, sala=sala):
                    voto = Voto(sesion=sesion, sala=sala, megusta=False)
                    voto.save()

            return redirect('manejar_salas', sala=nombre_sala)
        else:
            return HttpResponse("Introduzca un nombre de sala válido por favor.")

def help(request):
    if 'cookie_user' in request.COOKIES:
        cookie_user = request.COOKIES['cookie_user']
        configuracion = Configuracion.objects.get(sesion__cookie_user=cookie_user)
    else:
        return redirect('login')
    form_sala = SalaForm(request.POST)
    total_mensajes_textuales, total_mensajes_imagenes, total_salas_activas = pie_pagina()

    template = loader.get_template('DeCharla/help.html')
    contexto = {
        'form_sala': form_sala,
        'configuracion': configuracion,
        'total_mensajes_textuales': total_mensajes_textuales,
        'total_mensajes_imagenes': total_mensajes_imagenes,
        'total_salas_activas': total_salas_activas,
    }
    return HttpResponse(template.render(contexto, request))


@receiver(post_save, sender=Sesion)
def crear_votos_sesion_existente(sender, instance, created, **kwargs):
    if created:
        salas = Sala.objects.all()
        for sala in salas:
            sala.save()
            Voto.objects.create(sesion=instance, sala=sala, megusta=False)

post_save.connect(crear_votos_sesion_existente, sender=Sesion)


@csrf_exempt
def index(request):
    if 'cookie_user' in request.COOKIES:
        cookie_user = request.COOKIES['cookie_user']
        configuracion = Configuracion.objects.get(sesion__cookie_user=cookie_user)
    else:
        return redirect('login')

    sala_list = Sala.objects.all()
    sesion_obj = Sesion.objects.get(cookie_user=cookie_user)
    salas_con_mensajes = []

    for sala in sala_list:
        num_mensajes = Mensaje.objects.filter(sala=sala).count()
        try:
            ultima_visita = UltimaVisita.objects.filter(sesion=sesion_obj, sala=sala).first()
            if ultima_visita:
                mensajes_no_leidos = Mensaje.objects.filter(sala=sala, fecha__gt=ultima_visita.last_visit).count()
                if mensajes_no_leidos > 0:
                    ultima_visita.mensajes_no_leidos = mensajes_no_leidos
                    ultima_visita.save()
            else:
                mensajes_no_leidos = num_mensajes

        except UltimaVisita.DoesNotExist:
            mensajes_no_leidos = num_mensajes

        salas_con_mensajes.append((sala, num_mensajes, mensajes_no_leidos))

    total_mensajes_textuales, total_mensajes_imagenes, total_salas_activas = pie_pagina()
    form_sala = SalaForm(request.POST)
    votos = Voto.objects.filter(sesion=sesion_obj)
    template = loader.get_template('DeCharla/index.html')
    contexto = {
        'sala_list': sala_list,
        'form_sala': form_sala,
        'votos': votos,
        'salas_con_mensajes': salas_con_mensajes,
        'configuracion': configuracion,
        'total_mensajes_textuales': total_mensajes_textuales,
        'total_mensajes_imagenes': total_mensajes_imagenes,
        'total_salas_activas': total_salas_activas,
    }
    return HttpResponse(template.render(contexto, request))


def pie_pagina():
    mensajes_textuales = Mensaje.objects.filter(es_url=False)
    mensajes_imagenes = Mensaje.objects.filter(es_url=True)
    total_mensajes_textuales = mensajes_textuales.count()
    total_mensajes_imagenes = mensajes_imagenes.count()
    total_salas_activas = Sala.objects.count()
    return total_mensajes_textuales, total_mensajes_imagenes, total_salas_activas

def doGET(sala, cookie_user, sala_obj):
    mensajes_list = Mensaje.objects.filter(sala__nombre=sala).order_by('-fecha')
    sesion_obj = get_object_or_404(Sesion, cookie_user=cookie_user)
    ultima_visita, created = UltimaVisita.objects.get_or_create(sesion=sesion_obj, sala=sala_obj)

    if created:
        mensajes_no_leidos = mensajes_list.count()
    else:
        mensajes_no_leidos = mensajes_list.filter(fecha__gt=ultima_visita.last_visit).count()

    ultima_visita.last_visit = timezone.now()
    ultima_visita.save()

    response = HttpResponse()
    cookie_key = 'last_visit_{}'.format(sala.replace(' ', '_'))
    response.set_cookie(cookie_key, timezone.now().strftime('%Y-%m-%d %H:%M:%S'))

    return mensajes_list, mensajes_no_leidos


def doPOST_mensaje(request, sesion, sala, sala_obj, configuracion):
    form = MensajeForm(request.POST)
    if form.is_valid():
        mensaje = form.save(commit=False)
        mensaje.sala = sala_obj
        mensaje.creador = configuracion.nombre
        mensaje.save()
        ultima_visita = UltimaVisita.objects.get(sesion=sesion, sala=sala_obj)
        ultima_visita.save()

        return redirect('manejar_salas', sala=sala)

def doPUT(request, sala):
    sala_obj = Sala.objects.get(nombre=sala)
    xml_data = request.body
    try:
        dom = minidom.parseString(xml_data)
        messages = dom.getElementsByTagName('message')

        for message in messages:
            is_image = message.getAttribute('isimg')
            text_elem = message.getElementsByTagName('text')[0]
            text = text_elem.firstChild.nodeValue.strip()
            author_elem = message.getElementsByTagName('author')[0]
            author = author_elem.firstChild.nodeValue.strip()
            mensaje = Mensaje(sala=sala_obj, contenido=text, es_url=(is_image == 'true'), creador=author)
            mensaje.save()
        return HttpResponse('Sala actualizada correctamente')

    except Exception:
        return HttpResponseBadRequest('Error en el formato del XML')

@csrf_exempt
def manejar_salas(request, sala):
    if 'cookie_user' in request.COOKIES:
        cookie_user = request.COOKIES['cookie_user']
        sesion = Sesion.objects.get(cookie_user=cookie_user)
        configuracion = Configuracion.objects.get(sesion__cookie_user=cookie_user)
        sala_obj = get_object_or_404(Sala, nombre=sala)
        mensajes_list, mensajes_no_leidos = doGET(sala, cookie_user, sala_obj)
        form_sala = SalaForm(request.POST)
        form = MensajeForm()

        if request.method == 'POST':
            doPOST_mensaje(request,sesion, sala, sala_obj, configuracion)

        if request.method == 'PUT':
            doPUT(request, sala)

        total_mensajes_textuales, total_mensajes_imagenes, total_salas_activas = pie_pagina()
        template = loader.get_template('DeCharla/sala.html')
        contexto = {
            'sala': sala,
            'mensajes_list': mensajes_list,
            'form': form,
            'mensajes_no_leidos': mensajes_no_leidos,
            'configuracion': configuracion,
            'total_mensajes_textuales': total_mensajes_textuales,
            'total_mensajes_imagenes': total_mensajes_imagenes,
            'total_salas_activas': total_salas_activas,
            'form_sala': form_sala,
        }
        return HttpResponse(template.render(contexto, request))
    else:
        if request.method == 'PUT':
            authorization_header = request.headers.get('Authorization')
            if authorization_header and authorization_header.startswith('Basic '):
                credentials = authorization_header[6:]
                try:
                    Contrasena.objects.get(contrasena=credentials)
                    expiration = timezone.now() + timedelta(days=3650)
                    auth_token = secrets.token_hex(16)
                    sesion = Sesion(cookie_user=auth_token)
                    sesion.save()
                    configuracion = configuracion_default(sesion)
                    configuracion.save()
                    response = HttpResponse('logeado')
                    response.status_code = 200
                    response.set_cookie('cookie_user', auth_token, expires=expiration)
                    doPUT(request, sala)
                    return response
                except Contrasena.DoesNotExist:
                    return HttpResponse('Unauthorized, porfavor autentiquese mediante login o bien incluya la '
                                        'cabecera AAuthorization con la contraseña válida', status=401)
        else:
            return redirect('login')

@csrf_exempt
def manejar_votos(request):
    if 'cookie_user' in request.COOKIES:
        cookie_user = request.COOKIES['cookie_user']
        form_action = request.POST.get('action')

        if form_action == 'votar/':
            sala = request.POST.get('sala')
            sala_obj = get_object_or_404(Sala, nombre=sala)
            sesion = get_object_or_404(Sesion, cookie_user=cookie_user)
            voto = get_object_or_404(Voto, sala=sala_obj, sesion=sesion)
            voto.megusta = True
            voto.save()
            sala_obj.votos += 1
            sala_obj.save()
            return redirect('index')

        elif form_action == 'desvotar/':
            sala = request.POST.get('sala')
            sala_obj = get_object_or_404(Sala, nombre=sala)
            sesion = get_object_or_404(Sesion, cookie_user=cookie_user)
            voto = get_object_or_404(Voto, sala=sala_obj, sesion=sesion)
            voto.megusta = False
            voto.save()
            sala_obj.votos -= 1
            sala_obj.save()
            return redirect('index')

        else:
            return HttpResponseBadRequest('Invalid form action.')

    else:
        return redirect('login')


def manejar_configuracion(request):
    if request.method == 'GET' or request.method == 'POST':
        if 'cookie_user' in request.COOKIES:
            cookie_user = request.COOKIES['cookie_user']
            configuracion = Configuracion.objects.get(sesion__cookie_user=cookie_user)
        else:
            return redirect('login')

        if request.method == 'POST':
            form = ConfiguracionForm(request.POST)
            if form.is_valid():
                configuracion.nombre = form.cleaned_data['nombre']
                configuracion.tamano_fuente = int(form.cleaned_data['tamano_fuente'])
                configuracion.tipo_fuente = form.cleaned_data['tipo_fuente']
                configuracion.save()
                return redirect('configuracion')

        else:
            form = ConfiguracionForm(initial={
                'nombre': configuracion.nombre,
                'tamano_fuente': str(configuracion.tamano_fuente),
                'tipo_fuente': configuracion.tipo_fuente
            })
        total_mensajes_textuales, total_mensajes_imagenes, total_salas_activas = pie_pagina()
        form_sala = SalaForm()
        template = loader.get_template('DeCharla/configuracion.html')
        contexto = {
            'form': form,
            'configuracion': configuracion,
            'total_mensajes_textuales': total_mensajes_textuales,
            'total_mensajes_imagenes': total_mensajes_imagenes,
            'total_salas_activas': total_salas_activas,
            'form_sala': form_sala,
        }
        return HttpResponse(template.render(contexto, request))