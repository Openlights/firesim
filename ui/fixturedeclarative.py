from PySide import QtCore, QtGui, QtDeclarative

from fixture import Fixture

class FixtureDeclarative(QtDeclarative.QDeclarativeItem):

    def __init__(self, parent = None):
        super(FixtureDeclarative, self).__init__(parent)
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.color = QtGui.QColor(100, 100, 100)
        self.setHeight(4)
        self.setWidth(128)
        self.dragging = False

    def paint(self, painter, options, widget):
        self.rect = QtCore.QRect(0, 0, self.width(), self.height())
        painter.fillRect(self.rect, QtGui.QColor(200, 200, 0))

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.setPos(event.scenePos())

    def mousePressEvent(self, event):
        self.dragging = True

    def mouseReleaseEvent(self, event):
        self.dragging = False