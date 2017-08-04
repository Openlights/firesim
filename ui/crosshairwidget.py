from __future__ import division
from past.utils import old_div

from PyQt5 import QtCore, QtGui
from PyQt5.QtQuick import QQuickItem, QQuickPaintedItem


class CrosshairWidget(QQuickPaintedItem):

    size = 20

    def __init__(self, canvas=None, pos=None, text=None, callback=None):
        super(CrosshairWidget, self).__init__(canvas)
        #self.setFlag(QQuickItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        self.color = QtGui.QColor(100, 100, 100)
        self.canvas = canvas
        self.dragging = False
        self.mouse_down = False
        self.hovering = False
        self.hidden = True
        self.drag_pos = None
        self.scene_x = 0.0
        self.scene_y = 0.0
        self.text = text
        self.callback = callback
        self.setZ(110)

        self.setWidth(self.size + 4)
        self.setHeight(self.size + 4)

        if pos:
            self.scene_x, self.scene_y = pos
            x, y = self.canvas.scene_to_canvas(pos[0], pos[1])
            self.setX(100)
            self.setY(100)

    def boundingRect(self):
        # Bigger than the actual handle so that the text gets erased
        return QtCore.QRectF(-(old_div((self.size + 4), 2)), -(old_div((self.size + 4), 2)), self.size + 50, self.size + 20)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(-(old_div(self.size, 2)), -(old_div(self.size, 2)), self.size, self.size)
        return path

    def paint(self, painter):
        if self.hidden:
            return

        if self.hovering:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 200, 255), 4, QtCore.Qt.SolidLine))
            painter.drawLine (0, old_div(self.size, 2), 0, -(old_div(self.size, 2)))
            painter.drawLine(-(old_div(self.size, 2)), 0, old_div(self.size, 2), 0)

        if self.isSelected() or self.mouse_down:
            painter.setPen(QtGui.QPen(QtGui.QColor(50, 100, 255, 180), 6, QtCore.Qt.SolidLine))
            painter.drawLine (0, old_div(self.size, 2), 0, -(old_div(self.size, 2)))
            painter.drawLine(-(old_div(self.size, 2)), 0, old_div(self.size, 2), 0)

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 50, 255), 2, QtCore.Qt.SolidLine))
        painter.drawLine (0, old_div(self.size, 2), 0, -(old_div(self.size, 2)))
        painter.drawLine(-(old_div(self.size, 2)), 0, old_div(self.size, 2), 0)

        if self.text:
            painter.drawText(5, 15, self.text)

    def hoverEnterEvent(self, event):
        if self.hidden:
            return
        self.setZ(50)

    def hoverLeaveEvent(self, event):
        self.hovering = False
        #self.hidden = not self.fixture.isSelected()
        self.update()

    def hoverMoveEvent(self, event):
        if self.hidden:
            return

        if self.shape().contains(event.pos()):
            self.hidden = False
            self.hovering = True
        else:
            self.hovering = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_down:
            self.dragging = True
            npos = (event.scenePos() - self.drag_pos)
            if self.canvas.sceneBoundingRect().contains(event.scenePos()):
                self.moveBy(npos.x(), npos.y())
            self.drag_pos = event.scenePos()
            if self.callback is not None:
                self.callback(self.pos())

    def mousePressEvent(self, event):
        self.mouse_down = True
        self.drag_pos = event.scenePos()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.mouse_down = False
        self.drag_pos = None
        if self.callback is not None:
            self.callback(self.pos())

    def mouseDoubleClickEvent(self, event):
        pass
