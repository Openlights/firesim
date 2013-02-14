from PySide import QtCore, QtGui, QtDeclarative


class DragHandleWidget(QtDeclarative.QDeclarativeItem):

    def __init__(self, canvas=None, fixture=None, pos=None):
        super(DragHandleWidget, self).__init__(canvas)
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setAcceptsHoverEvents(True)
        self.color = QtGui.QColor(100, 100, 100)
        self.setHeight(32)
        self.setWidth(32)
        self.canvas = canvas
        self.fixture = fixture
        self.dragging = False
        self.mouse_down = False
        self.hovering = False
        self.drag_pos = None
        self.rect = QtCore.QRect(0, 0, 16, 16)
        if pos:
            self.setPos(pos[0], pos[1])

    def paint(self, painter, options, widget):
        if self.hovering:
            painter.setPen(QtGui.QColor(50, 100, 255, 255))
            painter.setBrush(QtGui.QColor(50, 100, 255, 255))
            hover_rect = QtCore.QRect(2, 2, 12, 12)
            painter.drawEllipse(hover_rect)
        fixture_bg = QtCore.QRect(4, 4, 8, 8)
        painter.setBrush(QtGui.QColor(0, 100, 200, 200))
        painter.drawEllipse(fixture_bg)

    def hoverEnterEvent(self, event):
        self.hovering = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hovering = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_down:
            self.dragging = True
            npos = (event.scenePos() - self.drag_pos)
            if self.canvas.sceneBoundingRect().contains(event.scenePos()):
                self.moveBy(npos.x(), npos.y())
            self.drag_pos = event.scenePos()

    def mousePressEvent(self, event):
        self.mouse_down = True
        self.drag_pos = event.scenePos()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.mouse_down = False
        self.drag_pos = None

    def mouseDoubleClickEvent(self, event):
        pass