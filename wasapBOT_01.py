#!/usr/bin/python3

import json
import mimetypes
import os
import time
import urllib.request
import pyperclip
import pyautogui
import pyscreenshot
import pytesseract
import requests
import difflib

from PIL import ImageChops
from datetime import datetime
import subprocess
import random

os.chdir('/home/wasap/whatsapp-bot')

DBG = 1
loc = 3

##########
# El ZOOM de la pagina esa en 125%
##########
pyautogui.FAILSAFE = True
urlimg = 'http://www.benteveo.com/siguit-inmo/images/'
imageFolder = "/home/cliff/Pictures/"

# COORDENADAS WASAP:
regionTelSup = (1117, 91, 1308, 125)  # El num de telefono que aparece arriba
posMsj1 = (854, 392)  # posicion del mensaje nuevo a la izquierda
posNewText = (1077, 652)  # El ultimo texto que manda el usuario en la zona de conversacion
regionNewText = (1039, 633, 1547, 679)  # Region donde aparece el ultimo texto
regionMessages = (660, 361, 1020, 712)  # zona donde estan todos los mensajes recibidos
regNewContact = (1242, 628, 1385, 660)  # Boton "NO ES SPAM" del cartel de spam
posBntNoEsSpam = (1321, 646)  # Posicion del boton de "NO ES SPAM"
regResFrame = (1527, 636, 1580, 677)  # Region donde aparece la X para cerrar un cuadro de respuesta
posResFrame = (1556, 656)


# COORDENADAS FILE MANAGER
posFolder = (262, 113)  # filemanager
posImg0 = (262, 113)  # Primer imagen en el filemanager
posTextBox = (1400, 400)  # caja donde se encuentra la conversacion

scrolling = (-2.1)


###########################################################


def nuevosmensajes(messagesframezone):
    im1 = pyscreenshot.grab(bbox=messagesframezone)
    time.sleep(3)
    im2 = pyscreenshot.grab(bbox=messagesframezone)
    diff = ImageChops.difference(im1, im2)

    if diff.getbbox():
        return True
    else:
        return False


###########################################################


def leernum(posmsj, reg):
    pyautogui.click(posmsj)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    return text.upper()


def leermsj(pos, reg):
    if DBG == 1: print('Func. Leer Msj')
    # im = pyscreenshot.grab(bbox=reg)

    pyautogui.click(x=pos[0], y=pos[1], clicks=3, interval=0.2)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    text = pyperclip.paste()
    pyperclip.copy('')
    return text.upper()
    # else:
    #     return ''


###########################################################


def guardar(tel):
    # TODO guardar el numero de telefono en la base de datos
    pass


###########################################################


def guardarfoto(url, path):
    print("guardando fotos")
    response = requests.get(url)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)

    img_data = requests.get(url).content
    with open(path + extension, 'wb') as handler:
        handler.write(img_data)


###########################################################


def ctrla():
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)


def copiarimg(regImg):
    print("copiando img")
    pyautogui.moveTo(regImg)
    pyautogui.click(regImg)
    time.sleep(1)
    ctrla()
    # Arrastro las imagenes
    pyautogui.moveTo(regImg, duration=1)
    pyautogui.dragTo(posTextBox[0], posTextBox[1], 2, button='left')
    time.sleep(8)
    pyautogui.press('enter')


###########################################################


def clearimg(dirpath):
    file_list = os.listdir(dirpath)
    for fileName in file_list:
        os.remove(dirpath + "/" + fileName)


###########################################################


def escribirrespuesta(msj):
    print("Escribiendo rta")
    print(msj)
    # pyautogui.click(posTextFrame)
    pyautogui.click(posMsj1)
    time.sleep(0.4)
    for letra in msj:
        if letra == 'ñ':
            copypaste('ñ')
        elif letra == 'á':
            copypaste('á')
        elif letra == 'é':
            copypaste('é')
        elif letra == 'í':
            copypaste('í')
        elif letra == 'ó':
            copypaste('ó')
        elif letra == 'ú':
            copypaste('ú')
        elif letra == 'ü':
            copypaste('ü')
        elif letra == ':':
            copypaste(':')
        elif letra == '/':
            copypaste('/')
        elif letra == '¿':
            copypaste('¿')
        elif letra == '?':
            copypaste('?')
        else:
            pyautogui.typewrite(letra)
        #time.sleep(0.05)
    pyautogui.press('enter')


def generarrespuesta(data_prop):
    rta = "Hola! Gracias por contactarte. En breve te enviamos los datos. \n"
    rta += data_prop
    return rta


def generarfooter(data, texto):
    print("Generando Footer")
    prod_nom = ""
    prod_tel = ""

    for i in data['schedule']:
        codigo = i["Cod"]
        if codigo in texto:
            prod_nom = i['prod_nom']
            prod_tel = i['prod_tel']

    return "Si te interesa esta propiedad comunicate con %s tel:%s " \
           "  \n ¿Te interesa otra propiedad? Pasanos el código." \
           % (prod_nom, prod_tel)


###########################################################


def copypaste(m):
    if DBG: print('F: Copypaste')
    pyperclip.copy(m)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')


###########################################################


def sync(loc):
    if DBG: print('F: Sync')
    command = 'rsync -Pavi -e "ssh -i %s/siguit.pem" --itemize-changes ' \
              'siguit@benteveo.com:/var/www/html/siguitds/inmobiliarias/schedule/cli-3.json ' % (os.getcwd())

    command += ' '+os.getcwd() + '/schedule.json'

    output, error = subprocess.Popen(
        command, universal_newlines=True, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if DBG: print(error)
    if DBG: print(output)
    if ".f" in output:
        return 0
    else:
        return 1


###########################################################


def obtenerpropiedades():
    with open('%s/schedule.json' % (os.getcwd())) as json_data:
        data = json.load(json_data)
        return data


###########################################################


def buscarporpropid(data, texto):
    print("buscando prop segun el texto que ingreso el cliente")
    texto = texto.upper()
    b = None
    # Debo encontrar un codigo valido
    for i in data['schedule']:
        codigo = i['Cod']
        if DBG: print('Codigo Disponible :' + codigo)
        # difflib.get_close_matches(codigo, texto.split())
        if codigo in texto:
            # if propid == i["reference_code"]:
            print("Prop Encontrada")
            b = "CODIGO: " + codigo + "\n"
            b += str(i["Descripcion"]) + "\n"
            b += "Direccion " + i["Direccion"] + "\n"
            b += "Precio " + str(i["Precio"]) + "\n"

            break
        else:
            # rtas = ['prop no encontrada', 'lo siento', 'no la encuentro']
            # b = random.choice(rtas)
            b = ''
    return b


###########################################################


def propimg(data, texto, fotodir):
    p = 0
    print("tomando data de fotos")
    for i in data['schedule']:
        codigo = i["Cod"]
        if codigo in texto:
            for entry in i['images']:
                p += 1
                # fotourl = i['photos'][p]['image']
                fotourl = entry['url']
                print(fotourl)
                guardarfoto(urlimg + fotourl, fotodir + str(p))
            break
    return p


###########################################################


def archivarchat():
    pyautogui.click(posMsj1, button='right')
    time.sleep(0.3)
    pyautogui.moveRel(100, 40)
    pyautogui.click()


###########################################################


def checkspam(pos, posbtnspam, reg):
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    if text.upper() == 'NO ES SPAM':
        pyautogui.click(posbtnspam)  # Voy a la posicion 1 y clickeo


###########################################################


def chkresframe(pos):
    if DBG: print('Fn: chkresframe')
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo


###########################################################





def run(force):
    # TODO corregir el tema de que cuando es cada 5 minutos busca a cada rato
    if nuevosmensajes(regionMessages) or force:
        print("Nuevo Mensaje")
        checkspam(posMsj1, posBntNoEsSpam, regNewContact)
        tel = leernum(posMsj1, regionTelSup)  # Leo el numero de telefono
        chkresframe(posResFrame)
        if tel:
            print("TEL: " + tel)
            texto = leermsj(posNewText, regionNewText)  # Obtengo el propid del mensaje del remitente
            if DBG == 1: print("TEXTO: " + texto)
            if len(texto) > 3:
                sync(loc)
                data = obtenerpropiedades()
                if data:
                    data_prop = buscarporpropid(data, texto)
                    if data_prop:
                        print(data_prop)
                        respuesta = generarrespuesta(data_prop)
                        escribirrespuesta(respuesta)
                        if propimg(data, texto, imageFolder):
                            print("Copiando Fotos")
                            copiarimg(posImg0)
                            clearimg(imageFolder)
                        time.sleep(4)
                        escribirrespuesta(generarfooter(data, texto))
                        if tel == leernum(posMsj1, regionTelSup):
                            archivarchat()


###########################################################


def test():
    pass
    # IAP21081


###########################################################


if __name__ == "__main__":
    lminute = 0
    while 1:
        minutes = int(datetime.now().strftime('%M'))
        if minutes % 5 == 0 and minutes != lminute:
            force = 1
            lminute = minutes
        else:
            force = 0
        run(force)
    #     time.sleep(0.5)
