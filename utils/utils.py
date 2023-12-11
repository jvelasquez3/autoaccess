import easyocr
import string

lector = easyocr.Reader(['es'], gpu=True)

dict_lecturas_int_incorrectas = {
    'O': '0',
    'D': '0',
    'Q': '0',
    'I': '1',
    'Z': '2',
    'J': '3',
    'A': '4',
    'S': '5',
    'G': '6',
    'B': '8'
}

dict_lecturas_char_incorrectas = {
    '0': 'D',
    '1': 'I',
    '2': 'Z',
    '7': 'J',
    '4': 'A',
    '5': 'S',
    '6': 'G',
    '8': 'B'
}


def leer_texto_placa(recorte_placa_bn):

    lecturas = lector.readtext(recorte_placa_bn)
    texto = ''

    for lectura in lecturas:
        box, texto, confianza = lectura
        texto = texto.upper().replace(" ", "")
        # print(texto)

        if texto != '' and es_formato_placa_gt(texto):
            texto = corregir_formato_gt(texto)

            if texto.startswith('H'):
                texto = 'M' + texto[1:]


            return texto, confianza, True
        

    return '', 0, False


def es_formato_placa_eu(texto):
    if len(texto) != 7:
        return False

    return es_letra(texto[0]) and es_letra(texto[1]) and es_numero(texto[2]) and es_numero(texto[3]) and es_letra(texto[4]) and es_letra(texto[5]) and es_letra(texto[6])


def es_formato_placa_gt(texto):
    if len(texto) != 7:
        return False

    return es_letra(texto[0]) and es_numero(texto[1]) and es_numero(texto[2]) and es_numero(texto[3]) and es_letra(texto[4]) and es_letra(texto[5]) and es_letra(texto[6])


def es_letra(caracter):
    return caracter in string.ascii_uppercase or caracter in dict_lecturas_char_incorrectas.keys()


def es_numero(caracter):
    return caracter in string.digits or caracter in dict_lecturas_int_incorrectas.keys()


def corregir_formato_eu(placa):

    nueva_placa = ''
    mapping = {0: dict_lecturas_char_incorrectas, 1: dict_lecturas_char_incorrectas, 2: dict_lecturas_int_incorrectas,
               3: dict_lecturas_int_incorrectas, 4: dict_lecturas_char_incorrectas, 5: dict_lecturas_char_incorrectas, 6: dict_lecturas_char_incorrectas}

    for i in range(7):
        if placa[i] in mapping[i].keys():
            nueva_placa += mapping[i][placa[i]]
        else:
            nueva_placa += placa[i]

    return nueva_placa


def corregir_formato_gt(placa):

    nueva_placa = ''
    mapping = {0: dict_lecturas_char_incorrectas, 1: dict_lecturas_int_incorrectas, 2: dict_lecturas_int_incorrectas,
               3: dict_lecturas_int_incorrectas, 4: dict_lecturas_char_incorrectas, 5: dict_lecturas_char_incorrectas, 6: dict_lecturas_char_incorrectas}

    for i in range(7):
        if placa[i] in mapping[i].keys():
            nueva_placa += mapping[i][placa[i]]
        else:
            nueva_placa += placa[i]

    return nueva_placa
