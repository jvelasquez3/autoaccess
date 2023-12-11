from django.urls import path
from .views import *

urlpatterns = [
    path('iniciar-reconocimiento/', iniciarReconocimiento, name='iniciar-reconocimiento'),
    path('iniciar-pregrabado/', iniciarPregrabado, name='iniciar-pregrabado'),
    path('autorizar-acceso/', autorizarAcceso, name='autorizar-acceso'),
]
