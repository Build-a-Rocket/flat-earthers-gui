from PyQt6.QtCore import QThread, pyqtSignal, QMetaObject
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton
from PyQt6 import uic, QtCore
from serial import Serial, unicode

from serial_thread import SerialThread


class UI(QWidget):

    def __init__(self):
        super().__init__()

        # loading the ui file with uic module
        uic.loadUi("gsw.ui", self)

        # Initiate serial port
        self.serial_port = Serial(None, 115200, dsrdtr=True)
        self.serial_port.port = "/dev/cu.usbmodem1101"

        # Initiate Serial Thread
        self.serialThread = SerialThread(self.serial_port)
        self._thread = QThread()
        self.serialThread.moveToThread(self._thread)

        self.serialThread.connectionSuccess.connect(self.connection_success)
        self.serialThread.connectionFailed.connect(self.connection_failed)
        self.serialThread.readFailed.connect(self.error_on_read)

        self._thread.started.connect(self.serialThread.run)

        self.allData = ""

        self._thread.start()

        self.outputBox = self.findChild(QTextEdit, "outputBox")
        self.serialThread.dataReceived.connect(self.updateOutputBox)

        self.sendButton = self.findChild(QPushButton, "sendButton")

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

                message = self.allData[s + 5:e + 3].split(',')
                self.allData = self.allData[e + 3:]

                telemetry = 'Altitude: %s\nTemperature: %s\n\n' % (message[1], message[2])

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
