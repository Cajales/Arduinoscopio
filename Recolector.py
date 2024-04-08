# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 00:23:00 2019

@author: javie
"""

import serial
import struct as sct
import win32com.client
import time as tm


class Canal():#vector para almacenar el dato y su tiempo de entrada
    def __init__(self,nombre):
        self.dato=[]
        self.time=tm.time()


class Recolector():#Clase que recolecta y guarda datos desde arduino 
    def __init__(self, Nch= 1, br = 115200):
        self.Nch = Nch
        self.br = br
        self.canales = []
        self.cantidad_datos = 10000
        self.num_bytes = 90
        self.last = 0
        self.pos=[] 
        self.ser = 0
        self.init_canales()
        
        
        
    def init_canales(self):    
        for i in range(0,self.Nch):       #inicia el vector de canales correspondientes a las entradas analogicas del arduino
            nombre=i                 #nombre corresponde al numero de la entrada analogica que se usara (considerando que se esta usando desde la 0 en adelante)
            a=Canal(nombre)          #objeto canal, almacena el dato y el tiempo de su entrada 
            self.canales.append(a)   #agrega el objeto canal al vector de canales
         
        
    def Conectar(self): #solo para windows, linux debe coenctar manualmente    
              
        #encuentra el puerto COM conectado,inicializa la coneccion con arduino,recibe el boudrate
        wmi = win32com.client.GetObject("winmgmts:")#encuentra el puerto COM conectado, asume que existe al menos un arduino conectado 
        print(len(wmi.InstancesOf("Win32_SerialPort")))

        for port in wmi.InstancesOf("Win32_SerialPort"): #recorre los puertos seriales de windows
            print("holi2")
            print (port.Name, port.DeviceID)
            if "serie" in port.Name:
                comPort = port.DeviceID
                print (comPort, "es Arduino")
                
                self.ser = serial.Serial(comPort, self.br, timeout=10) #inicializa la coneccion cor arduino (revisar que el rate bounds coinsida o se podria usar el maximo permitido para abarcar todos los posibles valores)
                self.ser.isOpen()
                self.ser.flushInput() 
        
    
    def Desconectar(self,ser):
        self.ser.close()
        print("Arduino Desconectado")

    
    
    
    def tomardatos(self):                                      #esta funcion recoje los datos y los guarda 
        val = 0                                             #esta variable guarda el dato entrante 
        first = False                                       #bandera para saber si el byte entrante es el primero o segundo del dato
        data=self.ser.read(self.num_bytes)                  #toma num_bytes datos del puerto serial
        vector=sct.unpack('%dB'%self.num_bytes,data)        # tranformacion de byte a int
        for i in vector:                                    #este for recorre el vector con los datos entrantes y los califica segun sean 
                                                             #print (i) #mostrar los datos disminuye la frecuencia de muestreo 
            if i<9:                                         #si el dato es menor a 9 es el nombre del canal al cual el dato corresponde
                self.pos.append(i)                          #agrega el nombre 
                self.last=i                                 #posicion del vector al que entrara un dato 
            elif 224 <= i <= 255:                            #si el el primer byte del valor
                val = (i & 0b11111) << 5
                first = True                                #si es verdadero el primer byte ya entro 
            elif 96 <= i <= 127:                             #si Aes el segundo byte del valor
                val |= (i & 0b11111)
                if first:                                   #como ahora first en verdadero 
                    self.canales[self.last].dato.append(val)#guarda el dato entrante en el vector que le corresponda
                    first=False
                             #cambia el valor de first
        
         
        
    def check(self):
        for j in range(0,self.Nch):                         #este for recorre el vector de canales verificando si alguno sobrepaso los 10000 datos
            if len(self.canales[j].dato)>self.cantidad_datos:             #si los sobre pasa los limpia para comenzar el grafico desde 0
                actual=tm.time()                            #toma el tiempo una vez que ya se han tomado los 10 mil datos
                tiempo=actual-self.canales[j].time          #calcula el tiempo transcurrido en los ultimos 10 mil datos tomados (esto para obtener una frecuencia relativa)
                self.canales[j].time=actual                 #actualiza el tiempo del ultimo calculo de frecuencia hasta los siguientes 10 mil datos
                print ("Frecuencia ",len(self.canales[j].dato)/tiempo, "[Hz]")
                del self.canales[j].dato[1:]                #limpia el vector donde se guardan los datos
                del self.pos[0:]
                                            #limpia el vector de datos entrantes

    def ultimodato(self):
        for j in range(0,self.Nch): 
            ultimo = len(self.canales[0].dato)-1
            n = self.canales[0].dato[ultimo]
        
        return n

    def guardar(self):
        
        archivo = []
        
        
        for j in range(0,self.Nch):    
            archivo.append(open("DatosFT " + j +".txt","w"))
            cadena=str(self.canales[0].dato)
            archivo.write(cadena)
            archivo.close()     