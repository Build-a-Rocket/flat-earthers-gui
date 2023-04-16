from PyQt6.QtCore import QThread, pyqtSignal, QMetaObject
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton
from PyQt6 import uic, QtCore
from pyqtgraph import PlotWidget
from serial import Serial, unicode

from serial_thread import SerialThread
from tele_graph import TelemetryGraph


class UI(QWidget):

    def __init__(self):
        super().__init__()

        # loading the ui file with uic module
        uic.loadUi("gsw.ui", self)

        # Initiate serial port
        
        #self.serial_port = Serial('/dev/cu.usbmodem1101', 2000000, dsrdtr=True)
        
        # unix
        self.serial_port = Serial('/dev/cu.usbmodem101', 2000000, dsrdtr=True)
        ####self.serial_port.port = "/dev/cu.usbmodem1101"

        # Initiate Serial Thread
        self.serialThread = SerialThread(self.serial_port)
        self._thread = QThread()
        self.serialThread.moveToThread(self._thread)

        self.serialThread.connectionSuccess.connect(self.connection_success)
        self.serialThread.connectionFailed.connect(self.connection_failed)
        self.serialThread.readFailed.connect(self.error_on_read)

        self._thread.started.connect(self.serialThread.run)

        self.allData = ""

        self.outputBox = self.findChild(QTextEdit, "outputBox")
        self.serialThread.dataReceived.connect(self.updateOutputBox)


        # SETUP GRAPHS       
        self.altitudeGraph = TelemetryGraph(self.findChild(PlotWidget, 'altitudeGraph'))
        self.altitudeGraph.setTitle('Altitude')
        self.altitudeGraph.addLine()
        
        self.tempGraph = TelemetryGraph(self.findChild(PlotWidget, 'tempGraph'))
        self.tempGraph.setTitle('Tempurature')
        self.tempGraph.addLine()
        
        self.accelGraph = TelemetryGraph(self.findChild(PlotWidget, 'accelGraph'))
        self.accelGraph.setTitle('Acceleration')
        self.accelGraph.addLine('x', 'red')
        self.accelGraph.addLine('y', 'blue')
        self.accelGraph.addLine('z', 'green')
       
        self.gyroGraph= TelemetryGraph(self.findChild(PlotWidget, 'gyroGraph'))
        self.gyroGraph.setTitle('Gyro')
        self.gyroGraph.addLine('x', 'red')
        self.gyroGraph.addLine('y', 'blue')
        self.gyroGraph.addLine('z', 'green')
        
        self.y = 0
        
        self.sendButton = self.findChild(QPushButton, "sendButton")
        
        self._thread.start()

    @QtCore.pyqtSlot()
    def connection_success(self):
        print("Connected!")

    @QtCore.pyqtSlot(str)
    def connection_failed(self, error):
        print(error)

    @QtCore.pyqtSlot(str)
    def error_on_read(self, error):
        print(error)

    @QtCore.pyqtSlot(bytes)
    def updateOutputBox(self, data):
        try:
            self.allData += unicode(data, errors='ignore')

            if self.allData.find('START') != -1 and self.allData.find('END') != -1:
                s = self.allData.find('START')
                e = self.allData.find('END')

                data = self.allData[s + 5:e + 3].split(',')
                self.allData = self.allData[e + 3:]

                telemetry = 'Altitude: %s\nTemperature: %s\n\n' % (data[1], data[2])
                
                #graph stuff!
                self.y += 1
                
                self.altitudeGraph.plotData(float(data[1]), self.y)
                
                self.tempGraph.plotData(float(data[2]), self.y)
                
                self.accelGraph.plotData(float(data[3]), self.y, 'x')
                self.accelGraph.plotData(float(data[4]), self.y, 'y')
                self.accelGraph.plotData(float(data[5]), self.y, 'z')
                
                self.gyroGraph.plotData(float(data[6]), self.y, 'x')
                self.gyroGraph.plotData(float(data[7]), self.y, 'y')
                self.gyroGraph.plotData(float(data[8]), self.y, 'z')
                
                
                self.outputBox.insertPlainText(telemetry)
                self.outputBox.ensureCursorVisible()

        except Exception as e:
            print(str(e))

    def closeEvent(self, event):
        self.serialThread.stop()
        self._thread.quit()
        self._thread.wait()


app = QApplication([])
window = UI()
window.show()
app.exec()
