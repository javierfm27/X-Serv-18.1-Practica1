#!/usr/bin/python3
"""
    Aplicacion Web que acorta la URL que se le introduzca por un formulario HTML,
    y esta es guardada en un diccionario. Es una aplicacion con estado, ya que cuando
    relanzamos el servidor una vez cerrado, las URL acortadas con el uso previo del
    servidor seguiran acortadas y asociadas a su direccion real

    Javier Fernandez Morata - ITT
"""

import webapp
import socket
import urllib.parse
import csv

class acortaURL(webapp.webApp):

    diccURL = {}
    diccNUM = {}
    fich = ''
    port = 0
    hostName = ''

    def readCsv(self, fichero):
        try:
            with open(fichero, 'r') as csvfile:
                urlReader = csv.reader(csvfile)
                for row in urlReader:
                    print("Hola")
        except IOError:
            csvfile = open(fichero,'w')
            csvfile.close()

    def saveURL(self, url):
        subcadena = urllib.parse.quote('https://',safe='') \
                    , urllib.parse.quote('http://',safe='')
        if url.startswith(subcadena) == True:
            urlOriginal = urllib.parse.unquote(url)
        else:
            urlOriginal = 'http://www.' + urllib.parse.unquote(url)
            print(urlOriginal)
        #Guardo en Diccionario y lo escribo en el csv
        num = len(self.diccURL)
        self.diccURL[urlOriginal] = num
        self.diccNUM[num] = urlOriginal
        with open(self.fich, 'w') as csvfile:
            urlWriter = csv.writer(csvfile , delimiter=' ', quotechar='|',quoting = csv.QUOTE_MINIMAL)
            urlWriter.writerow(urlOriginal + str(num))
        csvfile.close()

    def getURL(self, url):
        subcadena = urllib.parse.quote('https://',safe='') \
                    , urllib.parse.quote('http://',safe='')
        if url.startswith(subcadena) == True:
            return urllib.parse.unquote(url)
        else:
            return 'http://www.' + urllib.parse.unquote(url)

    def processGET(self, rec):
        if rec == "/":
            httpCode = "200 OK"
            htmlAnswer = "<!DOCTYPE html><html><body> " \
                + "<form id='formulario' method='post'> " \
                + "<label>Introduce la URL que desea acortar</br></label>" \
                + "<input name='url' type='text'> " \
                + "<input type='submit' value='Enviar'></form>" \
                + " Estas son las URLS que se han acortado <br>" \
                + str(self.diccURL) \
                + "</body></html>"
        else:
            num = rec[1:]
            if int(num) in self.diccNUM:
                urlOriginal = self.diccNUM[int(num)]
                httpCode = "301 Moved Permanently \r\n" \
                        + "Location: " + urlOriginal
                htmlAnswer = "<!DOCTYPE html><html><body> " \
                            + " Va a ser redirigido </body></html>"
            else:
                httpCode = "404 Not Found"
                htmlAnswer = "<!DOCTYPE html><html><body> " \
                            + "No existe URL para ese recurso" \
                            + "</body></html>"
        return (httpCode, htmlAnswer)

    def processPOST(self, url):
        if isinstance(url, int) == True:
            httpCode = "400 Bad Request"
            htmlAnswer = "<!DOCTYPE html><html><body> " \
                + "<h3>ERROR! Debe introducir una URL</h3>" \
                + "</body></html>"
        else:
            if not(urllib.parse.unquote(url) in self.diccURL):
                self.saveURL(url)
            httpCode = "200 Ok"
            urlTraducida = self.getURL(url)
            urlAcortada = "http://" + self.hostName + ":" + str(self.port) \
                        + "/" + str(self.diccURL[urlTraducida])
            htmlAnswer = "<!DOCTYPE html><html><body> Estas son las URLs<br>" \
                        + "Original: <a href='" + urlTraducida \
                        + "'> " + urlTraducida + "</a><br>"  \
                        + "Acortada: <a href='" + urlAcortada  \
                        + "'> " + urlAcortada + "</a>" \
                        + "</body></html>"
        return (httpCode, htmlAnswer)

    def parse(self, request):
        #Devuelve el contenido de la peticion que nos interesa, con "/incluida, el metodo HTTP y URL si la hubiera"
        if request != '':
            queryString = request.split()[-1]
            queryString = queryString.split('=')
            url = 0
            if queryString[0] == "url":
                if queryString[1] != "":
                    url = queryString[1]
            parsedRequest = request.split()[0], request.split()[1], url
            return parsedRequest
        else:
            return None

    def process(self, parsedRequest):
        if parsedRequest != None:
            method, rec, url = parsedRequest
            if method == 'GET':
                httpCode, htmlAnswer = self.processGET(rec)
            elif method == 'POST':
                httpCode, htmlAnswer = self.processPOST(url)
            return (httpCode, htmlAnswer)
        else:
            return ("400 Bad Request", "<html><body> Peticion Inexistente </body></html>")

    def __init__(self, host, port, fich):
        self.port = port
        self.hostName = host
        self.fich = fich
         #self.readCsv(fich)
        webapp.webApp.__init__(self, host, port)

if __name__ == "__main__":
    fich = input("Introduce el fichero donde se almacenan las URLS--> ")
    testApp = acortaURL('localhost',1232,fich)
