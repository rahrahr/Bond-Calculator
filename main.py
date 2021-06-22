import sys
from gui import Ui
from PyQt5 import QtWidgets, uic
import os

if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    sys.argv += ['--style', 'fusion']
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec()
