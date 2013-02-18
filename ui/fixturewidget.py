import logging as log

from PySide import QtCore, QtGui, QtDeclarative

from draghandlewidget import DragHandleWidget


class FixtureWidget(QtDeclarative.QDeclarativeItem):

    def __init__(self, canvas=None, id=0, model=None, move_callback=None):
        super(FixtureWidget, self).__init__(canvas)
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton | QtCore.Qt.MouseButton.MiddleButton | QtCore.Qt.MouseButton.RightButton)
        self.setAcceptsHoverEvents(True)
        self.color = QtGui.QColor(100, 100, 100)
        self.id = id
        self.model = model
        self.about_to_delete = False
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

    def deleteLater(self):
        self.drag1.deleteLater()
        self.drag2.deleteLater()
        super(FixtureWidget, self).deleteLater()

    def update_geometry(self):
        self.width = int(self.model.pos2[0] - self.model.pos1[0])
        self.height = int(self.model.pos2[1] - self.model.pos1[1])
        self.prepareGeometryChange()
        self.update(self.boundingRect())

    def boundingRect(self):
        """Defines an outer bounding rectangle, used for repaint only"""
        if self.width >= 0 and self.height >= 0:
            return QtCore.QRectF(-8, -8, self.width + 16, self.height + 16)
        elif self.width >= 0 and self.height < 0:
            return QtCore.QRectF(-8, self.height - 8, self.width + 16, -self.height + 16)
        elif self.width < 0 and self.height >= 0:
            return QtCore.QRectF(self.width - 8, -8, -self.width + 16, self.height + 16)
        else:
            return QtCore.QRectF(self.width - 8, self.height - 8, -self.width + 16, -self.height + 16)

    def shape(self):
        """Defines a 4-gon for mouse selection/hovering, larger than the drawn fixture"""
        path = QtGui.QPainterPath()
        line = QtCore.QLineF(0, 0, self.width, self.height)
        offset1 = line.normalVector().unitVector()
        offset1.setLength(10)
        ol1 = QtCore.QLineF(0, 0, self.width, self.height)
        ol1.translate(offset1.dx(), offset1.dy())
        ol2 = QtCore.QLineF(0, 0, self.width, self.height)
        ol2.translate(-offset1.dx(), -offset1.dy())

        p = QtGui.QPolygonF([
            QtCore.QPoint(ol1.x1(), ol1.y1()),
            QtCore.QPoint(ol1.x2(), ol1.y2()),
            QtCore.QPoint(ol2.x2(), ol2.y2()),
            QtCore.QPoint(ol2.x1(), ol2.y1())
        ])

        path.addPolygon(p)
        path.closeSubpath()
        return path

    def paint(self, painter, options, widget):
        painter.setBrush(QtGui.QColor(0, 0, 0, 0))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 200), 6, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(0, 0, self.width, self.height)
        if self.isSelected() or self.hovering:
            if not self.about_to_delete:
                painter.setPen(QtGui.QPen(QtGui.QColor(50, 100, 255, 225), 10, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            else:
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 50, 50, 225), 10, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            painter.drawLine(0, 0, self.width, self.height)
        #painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 0, 255), 1, QtCore.Qt.DashLine))
        #painter.drawPath(self.shape())

        if self.model.pixels > 0:
            color_line = QtCore.QLineF(0, 0, self.width, self.height)
            color_line.setLength(color_line.length() / self.model.pixels)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))

            for pixel in self.model.pixel_data:
                px, py = color_line.x1(), color_line.y1()
                r, g, b = pixel[0], pixel[1], pixel[2]
                painter.setBrush(QtGui.QColor(r, g, b, 255))
                painter.drawEllipse(QtCore.QPointF(px, py), 2, 2)
                color_line.translate(color_line.dx(), color_line.dy())

        if self.model.controller.scene.get("labels_enable", False):
            x = self.width / 2 - 16
            y = self.height / 2 - 8
            label_font = QtGui.QFont()
            label_font.setPointSize(8)
            painter.setFont(label_font)
            label_rect = QtCore.QRectF(x, y, 32, 16)
            painter.setBrush(QtGui.QColor(128, 64, 128, 180))
            painter.setPen(QtGui.QColor(100, 100, 100, 100))
            painter.drawRoundedRect(label_rect, 5, 5)
            painter.setPen(QtGui.QColor(255, 255, 255, 255))
            painter.drawText(label_rect, QtCore.Qt.AlignCenter, "%d:%d" % (self.model.strand, self.model.address))

    def hoverEnterEvent(self, event):
        self.setZValue(1)
        if self.shape().contains(event.pos()):
            self.hovering = True
            self.drag1.hovering = True
            self.drag2.hovering = True
            self.drag1.hidden = False
            self.drag2.hidden = False
        #else:
        #    self.hovering = False
        #    self.drag1.hovering = False
        #    self.drag2.hovering = False
        #    self.drag1.hidden = not self.isSelected()
        #    self.drag2.hidden = not self.isSelected()

        self.drag1.update()
        self.drag2.update()
        self.update()
        event.ignore()

    def hoverLeaveEvent(self, event):
        self.setZValue(0)
        self.hovering = False
        self.drag1.hovering = False
        self.drag2.hovering = False
        self.drag1.hidden = not self.isSelected()
        self.drag2.hidden = not self.isSelected()
        self.drag1.update()
        self.drag2.update()
        event.ignore()

    def hoverMoveEvent(self, event):
        if self.shape().contains(event.pos()):
            self.setZValue(50)
            self.drag1.setZValue(50)
            self.drag2.setZValue(50)
            self.hovering = True
            self.drag1.hovering = True
            self.drag2.hovering = True
            self.drag1.hidden = False
            self.drag2.hidden = False
        else:
            self.hovering = False
            if not self.isSelected():
                self.setZValue(0)
                self.drag1.setZValue(0)
                self.drag2.setZValue(0)
            self.drag1.hovering = False
            self.drag2.hovering = False
            self.drag1.hidden = not self.isSelected()
            self.drag2.hidden = not self.isSelected()

        self.drag1.update()
        self.drag2.update()
        self.update()
        event.ignore()

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

    def select(self, selected, multi=False):
        self.drag1.setSelected(selected)
        self.drag2.setSelected(selected)
        self.setSelected(selected)
        if selected:
            self.setZValue(100)
            self.drag1.setZValue(150)
            self.drag2.setZValue(150)
            self.drag1.hidden = False
            self.drag2.hidden = False
        else:
            self.setZValue(0)
            self.drag1.setZValue(0)
            self.drag2.setZValue(0)
            self.drag1.hidden = True
            self.drag2.hidden = True
        self.drag1.update()
        self.drag2.update()

    def mouseReleaseEvent(self, event):
        if not self.dragging:
            if event.button() == QtCore.Qt.MouseButton.LeftButton and self.shape().contains(event.pos()):
                self.select(not self.isSelected())
                # TODO: Implement multi-select with control or shift key
                multi = False
                self.model.controller.widget_selected(self.isSelected(), self.model, multi)
                self.canvas.on_fixture_click(self)

        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            if not self.about_to_delete:
                self.about_to_delete = True
            else:
                self.model.request_destruction()
        else:
            self.about_to_delete = False

        if event.button() == QtCore.Qt.MouseButton.RightButton:
            pass

        self.dragging = False
        self.mouse_down = False
        self.drag_pos = None
        if self.move_callback:
            self.move_callback(self)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.model.random_color()

    def handle_callback(self, handle):
        if handle == self.drag1:
            self.model.pos1 = [int(handle.pos().x()), int(handle.pos().y())]
            self.setPos(handle.pos())
        else:
            self.model.pos2 = [int(handle.pos().x()), int(handle.pos().y())]
        self.update_geometry()