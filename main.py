import sys
from gui import Ui
from PyQt5 import QtWidgets, uic

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec()
