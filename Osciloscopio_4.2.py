# -*- coding: utf-8 -*-
"""
Created on Fri May 17 01:15:46 2019

@author: Ignacio
"""

import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.uic import loadUi
import Recolector
import pyqtgraph as pg

class Osciloscopio(QWidget):
    def __init__(self):
        super(Osciloscopio, self).__init__()
        self.init_ui()

    def init_ui(self):
        loadUi('Osciloscopio.ui', self)
        self.arduino = Recolector.Recolector()

        self.pushButton.clicked.connect(self.arduino.Conectar)
        self.pushButton_2.clicked.connect(self.arduino.Desconectar)
        self.pushButton_3.clicked.connect(self.on)
        self.pushButton_4.clicked.connect(self.off)

        self.plotWidget = pg.PlotWidget()
        self.p = []
        self.linea = []
        self.verticalLayout.addWidget(self.plotWidget)
        self.bandera = False
        self.frecuencia = 0
        self.fft_linea = []
        self.init_graficos()

        self.bandera_reinicio = False

    @pyqtSlot()
    def init_graficos(self):
        self.p = [self.plotWidget.plot(pen=pg.mkPen('b')) for _ in range(self.arduino.Nch)]
        self.linea = self.p
        
        for i in range(self.arduino.Nch):
            self.plotWidget.setYRange(0, 1024, i)
            self.plotWidget.setXRange(0, self.arduino.cantidad_datos, i)

    def Actualizar_graficos(self):
        for i in range(self.arduino.Nch):
            self.linea[i].setData(self.arduino.canales[i].dato)
            if self.bandera_reinicio:
                self.linea[(i + 1) % self.arduino.Nch].setData(self.fft_linea)
        QApplication.processEvents()

    def on(self):
        self.bandera = True
        while self.bandera:
            self.arduino.tomardatos()
            self.Actualizar_graficos()
            self.bandera_reinicio = self.arduino.check()
            if self.bandera_reinicio:
                self.getFFT()

    def off(self):
        self.bandera = False

    def getFFT(self):
        self.fft_linea = self.arduino.fast_ft
        self.frecuencia = self.arduino.frecuencia

    def iniciar_graficofft(self):
        self.p.append(self.plotWidget.plot(pen=pg.mkPen('b')))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Osciloscopio()
    widget.show()
    sys.exit(app.exec_())
