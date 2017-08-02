from PyQt5.QtCore import Qt, QPoint, QPointF, QSizeF, QRect
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF, QFont
from PyQt5.QtQuick import QQuickItem, QQuickPaintedItem


class DragHandleWidget(QQuickPaintedItem):

    def __init__(self, canvas, fixture, pos=None):
        super(DragHandleWidget, self).__init__(canvas)
        self.setFlag(QQuickItem.ItemHasContents, True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        self.color = QColor(100, 100, 100)
        self.canvas = canvas
        self.fixture = fixture
        self.setParent(fixture)
        self.dragging = False
        self.mouse_down = False
        self.hovering = False
        self.hidden = True
        self.drag_pos = None
        self.scene_x = 0.0
        self.scene_y = 0.0
        self._shape = None

        self.setWidth(48)
        self.setHeight(48)

        if pos:
            self.scene_x, self.scene_y = pos
            x, y = self.canvas.scene_to_canvas(pos[0], pos[1])
            self.setX(x)
            self.setY(y)

    def shape(self):
        if self._shape is None:
            origin = self.fixture.SHAPE_MARGIN
            path = QPainterPath()
            path.addEllipse(origin - 7, origin - 7, 14, 14)
            self._shape = path
        return self._shape

    def paint(self, painter):
        if self.hidden:
            return

        origin = self.fixture.SHAPE_MARGIN

        painter.setPen(QPen(QColor(255, 255, 0, 225),
                                  1,
                                  Qt.SolidLine,
                                  Qt.RoundCap,
                                  Qt.RoundJoin))
        if self.hovering:
            painter.setPen(QPen(QColor(255, 0, 255, 225),
                                  1,
                                  Qt.SolidLine,
                                  Qt.RoundCap,
                                  Qt.RoundJoin))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        #painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(50, 100, 255, 255), 2, Qt.SolidLine))
        if self.hovering:
            painter.setBrush(QColor(50, 100, 255, 255))
            hover_rect = QRect(origin - 6, origin - 6, 12, 12)
            painter.drawEllipse(hover_rect)
        if self.fixture.selected:
            painter.setBrush(QColor(0, 0, 0, 180))
            painter.setPen(QColor(100, 100, 100, 100))
            painter.drawRoundedRect(20, 20, 15, 18, 5, 5)
            painter.setPen(QColor(255, 255, 255, 255))
            if self == self.fixture.drag1:
                painter.drawText(-10, -12, "1")
            else:
                painter.drawText(-10, -12, "2")
        fixture_bg = QRect(origin - 4, origin - 4, 8, 8)
        painter.setBrush(QColor(50, 50, 100, 127))
        painter.drawEllipse(fixture_bg)

    def hoverEnterEvent(self, event):
        if (self.canvas.gui.state.locked or
            (not self.fixture.hovering and
            not self.fixture.selected)):
            return
        self.hovering = True
        self.setZ(150)

    def hoverLeaveEvent(self, event):
        if self.hovering:
            self.hovering = False
            #self.hidden = not self.fixture.isSelected()
            self.update()

    def hoverMoveEvent(self, event):
        if (self.canvas.gui.state.locked or
            (not self.fixture.hovering and
            not self.fixture.selected)):
            return
        if self.shape().contains(event.pos()):
            self.hidden = False
            self.hovering = True
        else:
            self.hovering = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_down and not self.canvas.gui.state.locked:
            self.dragging = True
            npos = (event.globalPos() - self.drag_pos)
            if self.canvas.contains(event.globalPos()):
                self.move_by(npos.x(), npos.y())
            self.drag_pos = event.globalPos()
            #self.update_positions()
            self.fixture.handle_move_callback(self)

    def mousePressEvent(self, event):
        self.mouse_down = True
        self.drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.mouse_down = False
        self.drag_pos = None
        self.update_positions()
        self.fixture.handle_move_callback(self)

    def mouseDoubleClickEvent(self, event):
        pass

    def update_positions(self):
        self.scene_x, self.scene_y = self.canvas.canvas_to_scene(self.x(), self.y())

    def move_by(self, x, y):
        self.moveBy(x, y)
        self.scene_x, self.scene_y = self.canvas.canvas_to_scene(self.x(), self.y())
