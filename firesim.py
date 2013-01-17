import sys
from PySide import QtCore, QtGui

from ui.firesimgui import Ui_FireSim


class FireSimController(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(FireSimController, self).__init__(parent)
        self.ui = Ui_FireSim()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    gui = FireSimController()
    gui.show()
    sys.exit(app.exec_())