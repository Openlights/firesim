from PySide import QtCore, QtGui, QtDeclarative


class SimCanvasDeclarative(QtDeclarative.QDeclarativeItem):
    def __init__(self, parent = None):
        super(SimCanvasDeclarative, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.color = QtGui.QColor(255, 255, 0)

    def paint(self, painter, options, widget):
        painter.fillRect(0, 0, self.width(), self.height(), QtGui.QColor(0, 0, 0))
        pen = QtGui.QPen(self.color, 2)
        painter.setPen(pen)
        painter.setRenderHints(QtGui.QPainter.Antialiasing, True)
        painter.drawPie(self.boundingRect(), 90 * 16, 290 * 16)

    def set_color(self, color):
        r, g, b = color
        self.color = QtGui.QColor(r, g, b)
        self.update()