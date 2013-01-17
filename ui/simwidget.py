from PySide import QtGui, QtCore

class SimWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(SimWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        pass
        self.setMinimumSize(100, 100)

    def paintEvent(self, e):
        qp = QtGui.QPainter(self)
        self.drawWidget(qp)

    def drawWidget(self, qp):
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.fillRect(self.rect(), QtGui.QColor(0, 0, 0))
