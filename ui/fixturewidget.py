from PySide import QtCore, QtGui, QtDeclarative


class FixtureWidget(QtDeclarative.QDeclarativeItem):

    def __init__(self, canvas=None, id=0, model=None, move_callback=None):
        super(FixtureWidget, self).__init__(canvas)
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setAcceptsHoverEvents(True)
        self.color = QtGui.QColor(100, 100, 100)
        self.id = id
        self.model = model
        self.move_callback = move_callback
        self.setHeight(16)
        self.setWidth(128)
        self.dragging = False
        self.mouse_down = False
        self.setSelected(False)
        self.hovering = False
        self.drag_pos = None
        self.rect = QtCore.QRect(0, 0, 128, 16)
        if canvas:
            self.canvas = canvas
            x, y = canvas.get_next_new_fixture_pos_and_increment()
            self.setPos(x, y)

    def paint(self, painter, options, widget):
        if self.isSelected() or self.hovering:
            painter.setPen(QtGui.QColor(50, 100, 255, 255))
            painter.setBrush(QtGui.QColor(50, 100, 255, 255))
            hover_rect = QtCore.QRect(2, 4, 124, 8)
            painter.drawRoundRect(hover_rect, 16, 16)
        fixture_bg = QtCore.QRect(4, 6, 120, 4)
        painter.fillRect(fixture_bg, QtGui.QColor(200, 200, 0, 200))

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
            if self.parent().sceneBoundingRect().contains(event.scenePos()):
                self.moveBy(npos.x(), npos.y())
            self.drag_pos = event.scenePos()
        #super(FixtureWidget, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self.mouse_down = True
        self.drag_pos = event.scenePos()
        #super(FixtureWidget, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.dragging:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.setSelected(not self.isSelected())
                if not self.isSelected():
                    self.hovering = False
                self.canvas.on_fixture_click(self)
        self.dragging = False
        self.mouse_down = False
        self.drag_pos = None
        if self.move_callback:
            self.move_callback(self.id, self.pos())
        #super(FixtureWidget, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(FixtureWidget, self).mouseDoubleClickEvent(event)