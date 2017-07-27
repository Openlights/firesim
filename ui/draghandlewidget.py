from PyQt5 import QtCore, QtGui
from PyQt5.QtQuick import QQuickItem, QQuickPaintedItem


class DragHandleWidget(QQuickPaintedItem):

    def __init__(self, canvas=None, fixture=None, pos=None):
        super(DragHandleWidget, self).__init__(canvas)
        self.setFlag(QQuickItem.ItemHasContents, True)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        self.color = QtGui.QColor(100, 100, 100)
        self.canvas = canvas
        self.fixture = fixture
        self.dragging = False
        self.mouse_down = False
        self.hovering = False
        self.hidden = True
        self.drag_pos = None
        self.scene_x = 0.0
        self.scene_y = 0.0
        #self.rect = QtCore.QRect(0, 0, 16, 16)
        if pos:
            self.scene_x, self.scene_y = pos
            x, y = self.canvas.scene_to_canvas(pos[0], pos[1])
            self.setX(x)
            self.setY(y)

    def boundingRect(self):
        # Bigger than the actual handle so that the text gets erased
        return QtCore.QRectF(-20, -26, 40, 40)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-6, -6, 12, 12)
        return path

    def paint(self, painter):
        if self.hidden:
            return
        #painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor(50, 100, 255, 255), 2, QtCore.Qt.SolidLine))
        if self.hovering:
            painter.setBrush(QtGui.QColor(50, 100, 255, 255))
            hover_rect = QtCore.QRect(-6, -6, 12, 12)
            painter.drawEllipse(hover_rect)
        if self.isSelected():
            painter.setBrush(QtGui.QColor(0, 0, 0, 180))
            painter.setPen(QtGui.QColor(100, 100, 100, 100))
            painter.drawRoundedRect(-14, -26, 15, 18, 5, 5)
            painter.setPen(QtGui.QColor(255, 255, 255, 255))
            if self == self.fixture.drag1:
                painter.drawText(-10, -12, "1")
            else:
                painter.drawText(-10, -12, "2")
        fixture_bg = QtCore.QRect(-4, -4, 8, 8)
        painter.setBrush(QtGui.QColor(100, 100, 100, 200))
        painter.drawEllipse(fixture_bg)

    def hoverEnterEvent(self, event):
        if (self.canvas.controller.scene.get("locked", False) or
            (self.fixture.hovering is False and
            self.fixture.isSelected() is False)):
            return
        self.setZValue(150)

    def hoverLeaveEvent(self, event):
        if (self.canvas.controller.scene.get("locked", False) or
            (self.fixture.hovering is False and
            self.fixture.isSelected() is False)):
            return
        self.hovering = False
        #self.hidden = not self.fixture.isSelected()
        self.update()

    def hoverMoveEvent(self, event):
        if (self.canvas.controller.scene.get("locked", False) or
            (self.fixture.hovering is False and
            self.fixture.isSelected() is False)):
            return
        if self.shape().contains(event.pos()):
            self.hidden = False
            self.hovering = True
        else:
            self.hovering = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_down and not self.fixture.model._controller.scene.get("locked", False):
            self.dragging = True
            npos = (event.scenePos() - self.drag_pos)
            if self.canvas.sceneBoundingRect().contains(event.scenePos()):
                self.move_by(npos.x(), npos.y())
            self.drag_pos = event.scenePos()
            #self.update_positions()
            self.fixture.handle_move_callback(self)

    def mousePressEvent(self, event):
        self.mouse_down = True
        self.drag_pos = event.scenePos()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.mouse_down = False
        self.drag_pos = None
        self.update_positions()
        self.fixture.handle_move_callback(self)

    def mouseDoubleClickEvent(self, event):
        pass

    def update_positions(self):
        self.scene_x, self.scene_y = self.canvas.canvas_to_scene(self.pos().x(), self.pos().y())

    def move_by(self, x, y):
        self.moveBy(x, y)
        self.scene_x, self.scene_y = self.canvas.canvas_to_scene(self.pos().x(), self.pos().y())
