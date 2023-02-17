from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget


class UI(QWidget):

    def __init__(self):
        super().__init__()

        # loading the ui file with uic module
        uic.loadUi("gsw.ui", self)

app = QApplication([])
window = UI()
window.show()
app.exec()
