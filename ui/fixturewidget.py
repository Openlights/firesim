from PySide import QtCore, QtGui, QtDeclarative

from draghandlewidget import DragHandleWidget


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
        #self.rect = QtCore.QRect(0, 0, 128, 16)
        if canvas:
            self.canvas = canvas
            x, y = canvas.get_next_new_fixture_pos_and_increment()
            #self.model.pos1 = [x, y]
            #self.model.pos2 = [x + 100, y]
            self.setPos(x, y)

        self.drag1 = DragHandleWidget(canvas=canvas, fixture=self, pos=self.model.pos1, move_callback=self.handle_callback)
        self.drag2 = DragHandleWidget(canvas=canvas, fixture=self, pos=self.model.pos2, move_callback=self.handle_callback)

        self.update_geometry()

        self.poly = QtGui.QPolygon([
            QtCore.QPoint(0, 0),
            QtCore.QPoint(self.width, 0),
            QtCore.QPoint(self.width, self.height),
            QtCore.QPoint(0, self.height)
        ])

    def update_geometry(self):
        self.width = int(self.model.pos2[0] - self.model.pos1[0])
        self.height = int(self.model.pos2[1] - self.model.pos1[1])
        self.prepareGeometryChange()
        self.update(self.boundingRect())

    def boundingRect(self):
        ws = self.width / max(1, abs(self.width))
        hs = self.height / max(1, abs(self.height))
        if self.width == 0:
            ws = 1
        if self.height == 0:
            hs = 1

        return QtCore.QRectF(ws * -8, hs * -8, self.width + (ws * 16), self.height + (hs * 16))

    def shape(self):
        path = QtGui.QPainterPath()
        xout =  (self.model.pos2[0] - self.model.pos1[0]) / max(1, abs(self.model.pos2[0] - self.model.pos1[0]))
        yout = -1 * (self.model.pos2[1] - self.model.pos1[1]) / max(1, abs(self.model.pos2[1] - self.model.pos1[1]))
        p = QtGui.QPolygonF([
            QtCore.QPoint(xout, yout),
            QtCore.QPoint(self.width - xout, self.height + yout),
            QtCore.QPoint(self.width + xout, self.height - yout),
            QtCore.QPoint(-xout, -yout)
        ])
        path.addPolygon(p)
        path.closeSubpath()
        return path

    def paint(self, painter, options, widget):

        painter.fillRect(self.boundingRect(), QtGui.QColor(255, 0, 0, 50))
        painter.setBrush(QtGui.QColor(0, 0, 0, 0))

        #painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 0, 200), 4, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(0, 0, self.width, self.height)
        if self.isSelected() or self.hovering:
            painter.fillRect(self.boundingRect(), QtGui.QColor(255, 255, 0, 50))
            painter.setPen(QtGui.QPen(QtGui.QColor(50, 100, 255, 200), 5, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            painter.drawLine(0, 0, self.width, self.height)
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 255, 255), 2, QtCore.Qt.DashLine))
        painter.drawPath(self.shape())

    def hoverEnterEvent(self, event):
        pass

    def hoverMoveEvent(self, event):
        if self.shape().contains(event.pos()):
            self.hovering = True
            self.drag1.hovering = True
            self.drag2.hovering = True
        else:
            self.hovering = False
            self.drag1.hovering = False
            self.drag2.hovering = False
        self.update()

    def hoverLeaveEvent(self, event):
        self.hovering = False
        self.drag1.hovering = False
        self.drag2.hovering = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.hovering and self.mouse_down:
            self.dragging = True
            npos = (event.scenePos() - self.drag_pos)
            if self.parent().sceneBoundingRect().contains(event.scenePos()):
                self.moveBy(npos.x(), npos.y())
                self.drag1.moveBy(npos.x(), npos.y())
                self.drag2.moveBy(npos.x(), npos.y())
            self.drag_pos = event.scenePos()
            if self.move_callback:
                self.move_callback(self)
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
            self.move_callback(self)
        #super(FixtureWidget, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(FixtureWidget, self).mouseDoubleClickEvent(event)

    def handle_callback(self, handle):
        if handle == self.drag1:
            self.model.pos1 = [int(handle.pos().x()), int(handle.pos().y())]
            self.setPos(handle.pos())
        else:
            self.model.pos2 = [int(handle.pos().x()), int(handle.pos().y())]
        self.update_geometry()