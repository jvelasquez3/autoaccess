from skimage.segmentation import clear_border
import pytesseract
import numpy as np
import imutils
import cv2
from utils.utils import *


def remover_ruido(gray, keep=5):
    # perform a blackhat morphological operation that will allow
    # us to reveal dark regions (i.e., text) on light backgrounds
    # (i.e., the license plate itself)
    # rectKern = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    # open = cv2.morphologyEx(gray, cv2.MORPH_OPEN, rectKern)
    open = cv2.dilate(gray, None, iterations=4)
    open = cv2.erode(open, None, iterations=4)
    return open


def remover_falsos_caracteres(gray, keep=5):
    # perform a blackhat morphological operation that will allow
    # us to reveal dark regions (i.e., text) on light backgrounds
    # (i.e., the license plate itself)
    # rectKern = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    # open = cv2.morphologyEx(gray, cv2.MORPH_OPEN, rectKern)
    open = cv2.erode(gray, None, iterations=6)
    open = cv2.dilate(open, None, iterations=6)
    return open


def biggest_contour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)

        if area > 5000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area

    return biggest, max_area


def reorder(points):
    points = points.reshape((4, 2))
    new_points = np.zeros((4, 1, 2), dtype=np.int32)
    add = points.sum(1)

    new_points[0] = points[np.argmin(add)]
    new_points[3] = points[np.argmax(add)]
    diff = np.diff(points, axis=1)
    new_points[1] = points[np.argmin(diff)]
    new_points[2] = points[np.argmax(diff)]

    return new_points


def realizar_lectura(placa):
    placa_recortada = recortar_rectangulo(placa)

    if placa_recortada is None:
        placa_recortada = placa

    # cv2.imshow('a analizar', placa)
    # cv2.waitKey(0)

    return leer_texto_placa(placa_recortada)


def recortar_rectangulo(placa):
    unused, placa_transformed_aux = cv2.threshold(
        placa, 64, 255, cv2.THRESH_BINARY_INV)

    contours, hierarchy = cv2.findContours(
        placa_transformed_aux, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    biggest, max_area = biggest_contour(contours)

    if biggest.size != 0:
        biggest = reorder(biggest)

        x, y, w, h = cv2.boundingRect(biggest)

        placa_transformed = placa[y:y+h, x:x+w]
        return placa_transformed

    return None
