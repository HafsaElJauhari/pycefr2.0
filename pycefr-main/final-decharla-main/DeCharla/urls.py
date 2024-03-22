from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('configuracion', views.manejar_configuracion, name='configuracion'),
    path('login', views.manejar_login, name='login'),
    path('logout', views.manejar_logout, name='logout'),
    path('help', views.help, name='help'),
    path('<str:sala>', views.manejar_salas, name='manejar_salas'),
    path('votar/', views.manejar_votos, name='manejar_votos'),
    path('desvotar/', views.manejar_votos, name='manejar_votos'),
    path('crear_sala/', views.crear_sala, name='crear_sala'),
    path('sala_json/<str:sala>', views.sala_json, name='sala_json'),
    path('sala_dinamica/<str:sala>', views.sala_dinamica, name='sala_dinamica'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
