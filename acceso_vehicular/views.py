from datetime import datetime, time, timedelta
import cv2
from django.shortcuts import render
from django.http import HttpResponse
from ultralytics import YOLO
from utils.utils import *
from utils.anpr import *
from django.template import Context, loader
from templates import *
from .models import *
from django.http import JsonResponse

# Create your views here.


detector_vehiculos = YOLO(
    './acceso_vehicular/models/yolov8n.pt')

tipos_vehiculos = {
    '2': 1,
    '3': 2,
    '5': 3,
    '7': 4
}

nombres_vehiculos = {
    '2': 'Automovil',
    '3': 'Motocicleta',
    '5': 'Bus',
    '7': 'Camión'
}

def iniciarPregrabado(request):
    
    detector_placas = YOLO(
        './acceso_vehicular/models/license_plate_detector.pt')

    cap = cv2.VideoCapture(
        './acceso_vehicular/resources/VID_20231208_224106471.mp4')
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    exito = True
    ultima_placa = ''

    while cap.isOpened():
        tipo_vehiculo = ''
        continuar_reconocimiento = True; 

        exito, captura = cap.read()
        if not exito or cap.get(cv2.CAP_PROP_POS_FRAMES) > total_frames:
            break

        cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + int(fps/2))

        detectar_vehiculo = request.GET.get('detectar_vehiculo', 'false') == 'true'
        tipo_acceso = request.GET.get('tipo_acceso', 'I')

        if detectar_vehiculo:
            continuar_reconocimiento = False
            detecciones_vehiculos = detector_vehiculos(captura)[0]
            
            for objeto in detecciones_vehiculos.boxes.data.tolist():
                unused, unused, unused, unused, unused, tipo_objeto = objeto

                if str(int(tipo_objeto)) in tipos_vehiculos.keys():
                    tipo_vehiculo = str(int(tipo_objeto))
                    continuar_reconocimiento = True
                    break

        detecciones_placas = detector_placas(captura)[0]

        area_grande = 0

        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0

        if continuar_reconocimiento and len(detecciones_placas.boxes.data.tolist()) > 0:

            for placa in detecciones_placas.boxes.data.tolist():
                xt1, yt1, xt2, yt2, score, tipo_objeto = placa

                if area_grande < (xt2 - xt1) * (yt2 - yt1):
                    area_grande = (xt2 - xt1) * (yt2 - yt1)
                    x1 = xt1
                    x2 = xt2
                    y1 = yt1
                    y2 = yt2

            placa = captura[int(y1):int(y2), int(x1):int(x2), :]
            placa_gris = cv2.cvtColor(placa, cv2.COLOR_BGR2GRAY)

            # ksize = (20, 20)

            # Using cv2.blur() method
            # recorte_placa_gris = cv2.blur(recorte_placa_gris, ksize)

            unused, placa_bn = cv2.threshold(
                placa_gris, 80, 255, cv2.THRESH_BINARY_INV)

            texto_placa, confianza, formato_correcto = realizar_lectura(
                placa_bn)
            
            prueba = False

            if (texto_placa != '' and ultima_placa != texto_placa and formato_correcto) or prueba:
                if prueba:
                    texto_placa = 'M942FJX'
                
                ultima_placa = texto_placa
                #cv2.imshow('placa_gris', placa_gris)
                #cv2.imshow('placa_bn', placa_bn)
                #cv2.waitKey(0)

                try:
                    horarios_filtrados = []
                    detalles_vehiculo = ''
                    vehiculo = Vehiculo.objects.get(placas = texto_placa)
                    horario = Horario.objects.filter(empleado = vehiculo.empleado.id)

                    hora_actual = datetime.now().time()
                    hora_actual_p30 = (datetime.now() + timedelta(minutes=30)).time()
                    hora_actual_m30 = (datetime.now() - timedelta(minutes=30)).time()

                    if tipo_acceso == 'I':
                        horarios_filtrados = [objeto for objeto in horario if objeto.hora_inicio <= hora_actual_p30 and objeto.hora_fin >= hora_actual and int(objeto.dia) == datetime.now().weekday() ]
                    else:
                        horarios_filtrados = [objeto for objeto in horario if objeto.hora_inicio <= hora_actual and objeto.hora_fin >= hora_actual_m30 and int(objeto.dia) == datetime.now().weekday() ]

                    horarios_dict = [objeto.to_dict() for objeto in horario]

                    if detectar_vehiculo and vehiculo.tipo.id != tipos_vehiculos[tipo_vehiculo]:
                        detalles_vehiculo = nombres_vehiculos[tipo_vehiculo]

                    autorizado = not vehiculo.empleado.validar_horario or len(horarios_filtrados) > 0

                    if autorizado and detalles_vehiculo == '':
                        tipo_acceso_db = TipoAcceso.objects.get(id=(1 if tipo_acceso == 'I' else 2))
                        acceso_registrar = LogAcceso(vehiculo = vehiculo, tipo_acceso = tipo_acceso_db, fecha_hora = datetime.now(), excepcion = False)
                        acceso_registrar.save()

                    data = {
                        'placa_detectada': True,
                        'es_empleado': True,
                        'autorizado': autorizado,
                        'detalles_vehiculo': detalles_vehiculo,
                        'vehiculo': vehiculo.to_dict(),
                        'horario': horarios_dict
                    }

                    cap.release()
                    return JsonResponse(data)
                except Vehiculo.DoesNotExist:
                    continue

            # placa_bn = remover_ruido(placa_bn)
            # texto_placa, confianza, formato_correcto = realizar_lectura(
            #     placa_bn)

            # if texto_placa != '' and ultima_placa != texto_placa and formato_correcto:
            #     ultima_placa = texto_placa
            #     # print("texto: " + texto_placa)
            #     #cv2.imshow('placa_gris', placa_gris)
            #     #cv2.imshow('placa_sin_ruido', placa_bn)
            #     #cv2.waitKey(0)
                
            #     try:
            #         vehiculo = Vehiculo.objects.get(placas = texto_placa)

            #         data = {
            #             'placa_detectada': True,
            #             'es_empleado': True,
            #             'autorizado': True,
            #             'vehiculo': vehiculo.to_dict()
            #         }

            #         cap.release()
            #         return JsonResponse(data)
            #     except Vehiculo.DoesNotExist:
            #         continue

            # placa_bn = remover_falsos_caracteres(
            #     placa_bn)
            # texto_placa, confianza, formato_correcto = realizar_lectura(
            #     placa_bn)

            # if texto_placa != '' and ultima_placa != texto_placa and formato_correcto:
            #     ultima_placa = texto_placa

            #     try:
            #         vehiculo = Vehiculo.objects.get(placas = texto_placa)

            #         data = {
            #             'placa_detectada': True,
            #             'es_empleado': True,
            #             'autorizado': True,
            #             'vehiculo': vehiculo.to_dict()
            #         }

            #         cap.release()
            #         return JsonResponse(data)
            #     except Vehiculo.DoesNotExist:
            #         continue
    
    cap.release()

    data = {
        'placa_detectada': ultima_placa != '',
        'es_empleado': False,
        'autorizado': False,
        'vehiculo': {'placas': ultima_placa}
    }

    return JsonResponse(data)

def iniciarReconocimiento(request):
    captura = captura_camara()
    continuar_reconocimiento = True
    
    if captura is not None:
        detector_placas = YOLO('./acceso_vehicular/models/license_plate_detector.pt')
        
        detectar_vehiculo = request.GET.get('detectar_vehiculo', 'false') == 'true'
        tipo_acceso = request.GET.get('tipo_acceso', 'I')
        tipo_vehiculo = ''

        if detectar_vehiculo:
            continuar_reconocimiento = False
            detecciones_vehiculos = detector_vehiculos(captura)[0]
            
            for objeto in detecciones_vehiculos.boxes.data.tolist():
                unused, unused, unused, unused, unused, tipo_objeto = objeto

                if str(int(tipo_objeto)) in tipos_vehiculos.keys():
                    tipo_vehiculo = str(int(tipo_objeto))
                    continuar_reconocimiento = True
                    break

        detecciones_placas = detector_placas(captura)[0]

        ultima_placa = ''
        area_grande = 0

        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0

        if len(detecciones_placas.boxes.data.tolist()) > 0 and continuar_reconocimiento:
            
            for placa in detecciones_placas.boxes.data.tolist():
                xt1, yt1, xt2, yt2, score, tipo_objeto = placa

                if area_grande < (xt2 - xt1) * (yt2 - yt1):
                    area_grande = (xt2 - xt1) * (yt2 - yt1)
                    x1 = xt1
                    x2 = xt2
                    y1 = yt1
                    y2 = yt2

            placa = captura[int(y1):int(y2), int(x1):int(x2), :]
            # cv2.imshow('placa_bn', placa)
            # cv2.waitKey(0)
            placa_gris = cv2.cvtColor(placa, cv2.COLOR_BGR2GRAY)

            # ksize = (20, 20)

            # Using cv2.blur() method
            # recorte_placa_gris = cv2.blur(recorte_placa_gris, ksize)

            unused, placa_bn = cv2.threshold(
                placa_gris, 150, 255, cv2.THRESH_BINARY_INV)

            texto_placa, confianza, formato_correcto = realizar_lectura(
                placa_bn)
            
            #print(texto_placa)
            
            if texto_placa != '' and ultima_placa != texto_placa and formato_correcto:
                ultima_placa = texto_placa
                #cv2.imshow('placa_gris', placa_gris)
                #cv2.imshow('placa_bn', placa_bn)
                #cv2.waitKey(0)

                try:
                    horarios_filtrados = []
                    detalles_vehiculo = ''
                    vehiculo = Vehiculo.objects.get(placas = texto_placa)
                    horario = Horario.objects.filter(empleado = vehiculo.empleado.id)

                    hora_actual = datetime.now().time()
                    hora_actual_p30 = (datetime.now() + timedelta(minutes=30)).time()
                    hora_actual_m30 = (datetime.now() - timedelta(minutes=30)).time()

                    if tipo_acceso == 'I':
                        horarios_filtrados = [objeto for objeto in horario if objeto.hora_inicio <= hora_actual_p30 and objeto.hora_fin >= hora_actual and int(objeto.dia) == datetime.now().weekday() ]
                    else:
                        horarios_filtrados = [objeto for objeto in horario if objeto.hora_inicio <= hora_actual and objeto.hora_fin >= hora_actual_m30 and int(objeto.dia) == datetime.now().weekday() ]

                    horarios_dict = [objeto.to_dict() for objeto in horario]

                    if detectar_vehiculo and vehiculo.tipo.id != tipos_vehiculos[tipo_vehiculo]:
                        detalles_vehiculo = nombres_vehiculos[tipo_vehiculo]

                    autorizado = not vehiculo.empleado.validar_horario or len(horarios_filtrados) > 0

                    if autorizado and detalles_vehiculo == '':
                        tipo_acceso_db = TipoAcceso.objects.get(id=(1 if tipo_acceso == 'I' else 2))
                        acceso_registrar = LogAcceso(vehiculo = vehiculo, tipo_acceso = tipo_acceso_db, fecha_hora = datetime.now(), excepcion = False)
                        acceso_registrar.save()

                    data = {
                        'placa_detectada': True,
                        'es_empleado': True,
                        'autorizado': autorizado,
                        'detalles_vehiculo': detalles_vehiculo,
                        'vehiculo': vehiculo.to_dict(),
                        'horario': horarios_dict
                    }

                    return JsonResponse(data)
                except Vehiculo.DoesNotExist:
                    data = {}

            # placa_bn = remover_ruido(placa_bn)
            # texto_placa, confianza, formato_correcto = realizar_lectura(
            #     placa_bn)
            #print(texto_placa)

            # if texto_placa != '' and ultima_placa != texto_placa and formato_correcto:
            #     ultima_placa = texto_placa
            #     # print("texto: " + texto_placa)
            #     #cv2.imshow('placa_gris', placa_gris)
            #     #cv2.imshow('placa_sin_ruido', placa_bn)
            #     #cv2.waitKey(0)
                
            #     try:
            #         vehiculo = Vehiculo.objects.get(placas = texto_placa)

            #         data = {
            #             'placa_detectada': True,
            #             'es_empleado': True,
            #             'autorizado': True,
            #             'vehiculo': vehiculo.to_dict()
            #         }

            #         return JsonResponse(data)
            #     except Vehiculo.DoesNotExist:
            #         data = {}

            # placa_bn = remover_falsos_caracteres(
            #     placa_bn)
            # texto_placa, confianza, formato_correcto = realizar_lectura(
            #     placa_bn)
            # #print(texto_placa)

            # if texto_placa != '' and ultima_placa != texto_placa and formato_correcto:
            #     ultima_placa = texto_placa

            #     try:
            #         vehiculo = Vehiculo.objects.get(placas = texto_placa)

            #         data = {
            #             'placa_detectada': True,
            #             'es_empleado': True,
            #             'autorizado': True,
            #             'vehiculo': vehiculo.to_dict()
            #         }

            #         return JsonResponse(data)
            #     except Vehiculo.DoesNotExist:
            #         data = {}

    data = {
        'placa_detectada': ultima_placa != '',
        'es_empleado': False,
        'autorizado': False,
        'vehiculo': {'placas': ultima_placa}
    }

    return JsonResponse(data)

def autorizarAcceso(request):
    tipo_acceso = request.GET.get('tipo_acceso', 'I')
    placas = request.GET.get('placas', '')
    
    vehiculo = Vehiculo.objects.get(placas = placas)
    tipo_acceso_db = TipoAcceso.objects.get(id=(1 if tipo_acceso == 'I' else 2))
    acceso_registrar = LogAcceso(vehiculo = vehiculo, tipo_acceso = tipo_acceso_db, fecha_hora = datetime.now(), excepcion = True)
    acceso_registrar.save()

    horario = Horario.objects.filter(empleado = vehiculo.empleado.id)
    horarios_dict = [objeto.to_dict() for objeto in horario]

    data = {
        'placa_detectada': True,
        'es_empleado': True,
        'autorizado': True,
        'detalles_vehiculo': '',
        'vehiculo': vehiculo.to_dict(),
        'horario': horarios_dict
    }

    return JsonResponse(data)

def captura_camara():
    # Capturar imagen de la cámara
    cap = cv2.VideoCapture(0)  # 0 representa la cámara predeterminada

    ret, frame = cap.read()
    cap.release()

    if ret:
        return frame
    
    return None