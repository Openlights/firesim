import logging as log

from PySide import QtCore, QtGui, QtDeclarative

from draghandlewidget import DragHandleWidget


class FixtureWidget(QtDeclarative.QDeclarativeItem):

    def __init__(self, canvas=None, model=None):
        super(FixtureWidget, self).__init__(canvas)
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton |
                                     QtCore.Qt.MouseButton.MiddleButton |
                                     QtCore.Qt.MouseButton.RightButton)
        self.setAcceptsHoverEvents(True)
        self.model = model
        self.about_to_delete = False
        self.setHeight(16)
        self.setWidth(128)
        self.dragging = False
        self.mouse_down = False
        self.setSelected(False)
        self.hovering = False
        self.bb_hovering = False
        self.drag_pos = None

        if canvas:
            self.canvas = canvas
            x, y = canvas.get_next_new_fixture_pos_and_increment()
            self.setPos(x, y)
            self.canvas.hover_move_event.connect(self.hover_move_handler)

        self.drag1 = DragHandleWidget(canvas=canvas, fixture=self, pos=self.model.pos1())
        self.drag2 = DragHandleWidget(canvas=canvas, fixture=self, pos=self.model.pos2())

        self.update_geometry()


    def deleteLater(self):
        self.drag1.deleteLater()
        self.drag2.deleteLater()
        super(FixtureWidget, self).deleteLater()

    def update_geometry(self):
        p1 = self.canvas.scene_to_canvas(self.model.pos1())
        p2 = self.canvas.scene_to_canvas(self.model.pos2())
        self.width = int(p2[0] - p1[0])
        self.height = int(p2[1] - p1[1])
        self.prepareGeometryChange()
        self.update(self.boundingRect())

    def boundingRect(self):
        """Defines an outer bounding rectangle, used for repaint only"""
        width, height = (self.canvas.coordinate_scale * self.width, self.canvas.coordinate_scale * self.height)
        if width >= 0 and height >= 0:
            return QtCore.QRectF(-8, -8, width + 16, height + 16)
        elif width >= 0 and height < 0:
            return QtCore.QRectF(-8, height - 8, width + 16, -height + 16)
        elif width < 0 and height >= 0:
            return QtCore.QRectF(width - 8, -8, -width + 16, height + 16)
        else:
            return QtCore.QRectF(width - 8, height - 8, -width + 16, -height + 16)

    def shape(self):
        """Defines a 4-gon for mouse selection/hovering, larger than the drawn fixture"""
        width, height = (self.canvas.coordinate_scale * self.width, self.canvas.coordinate_scale * self.height)
        path = QtGui.QPainterPath()
        line = QtCore.QLineF(0, 0, width, height)
        offset1 = line.normalVector().unitVector()
        offset1.setLength(7)
        ol1 = QtCore.QLineF(0, 0, width, height)
        ol1.translate(offset1.dx(), offset1.dy())
        ol2 = QtCore.QLineF(0, 0, width, height)
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
        width, height = (self.canvas.coordinate_scale * self.width, self.canvas.coordinate_scale * self.height)
        if self.hovering:
            painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 255, 225),
                                      12,
                                      QtCore.Qt.SolidLine,
                                      QtCore.Qt.RoundCap,
                                      QtCore.Qt.RoundJoin))
            painter.drawLine(0, 0, width, height)

        painter.setBrush(QtGui.QColor(0, 0, 0, 0))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 60),
                                  6,
                                  QtCore.Qt.SolidLine,
                                  QtCore.Qt.RoundCap,
                                  QtCore.Qt.RoundJoin))
        painter.drawLine(0, 0, width, height)
        if self.isSelected():
            if self.about_to_delete:
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 50, 50, 225),
                                          10,
                                          QtCore.Qt.SolidLine,
                                          QtCore.Qt.RoundCap,
                                          QtCore.Qt.RoundCap,
                                          QtCore.Qt.RoundJoin))
            else:
                painter.setPen(QtGui.QPen(QtGui.QColor(50, 100, 255, 225),
                                          10,
                                          QtCore.Qt.SolidLine,
                                          QtCore.Qt.RoundCap,
                                          QtCore.Qt.RoundJoin))
            painter.drawLine(0, 0, width, height)

        #if self.bb_hovering:
        #    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 0, 255), 1, QtCore.Qt.DashLine))
        #    painter.drawPath(self.shape())

        if self.model.pixels() > 0:
            color_line = QtCore.QLineF(0, 0, width, height)
            color_line.setLength(color_line.length() / self.model.pixels())
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))

            for pixel in self.model._pixel_data:
                px, py = color_line.x1(), color_line.y1()
                r, g, b = pixel[0], pixel[1], pixel[2]
                painter.setBrush(QtGui.QColor(r, g, b, 255))
                painter.setPen(QtGui.QPen(QtGui.QColor(r, g, b, 60),
                                          5,
                                          QtCore.Qt.SolidLine))
                painter.drawEllipse(QtCore.QPointF(px, py), 1.5, 1.5)
                #painter.drawLine(color_line.unitVector())
                color_line.translate(color_line.dx(), color_line.dy())

        if self.hovering or self.isSelected() or self.model._controller.scene.get("labels_enable", False):
            x = width / 2 - 12
            y = height / 2 - 7
            label_font = QtGui.QFont()
            label_font.setPointSize(8)
            painter.setFont(label_font)
            label_rect = QtCore.QRectF(x, y, 24, 14)
            painter.setBrush(QtGui.QColor(128, 64, 128, 220))
            painter.setPen(QtGui.QColor(100, 100, 100, 100))
            painter.drawRoundedRect(label_rect, 5, 5)
            painter.setPen(QtGui.QColor(255, 255, 255, 255))
            painter.drawText(label_rect, QtCore.Qt.AlignCenter, "%d:%d" % (self.model.strand(), self.model.address()))

    def hoverEnterEvent(self, event):
        self.bb_hovering = True
        #self.setZValue(1)
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
        #event.ignore()

    def hoverLeaveEvent(self, event):
        self.bb_hovering = False
        self.setZValue(0)
        self.hovering = False
        self.drag1.hovering = False
        self.drag2.hovering = False
        self.drag1.hidden = not self.isSelected()
        self.drag2.hidden = not self.isSelected()
        self.drag1.update()
        self.drag2.update()
        #event.ignore()

    def hoverMoveEvent(self, event):
        self.hover_move_handler(None, None, e=event)

    def hover_move_handler(self, widget, pos, e=None):
        if widget is self:
            return

        if e is not None:
            pos = e.pos()
        else:
            pos = self.mapFromScene(pos)

        #self.bb_hovering = True
        if self.shape().contains(pos):
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
            if widget is None:
                self.canvas.propagate_hover_move(self, e.scenePos())

        self.drag1.update()
        self.drag2.update()
        self.update()

    def mouseMoveEvent(self, event):
        if self.hovering and self.mouse_down and not self.model._controller.scene.get("locked", False):
            self.dragging = True
            npos = (event.scenePos() - self.drag_pos)
            if self.parent().sceneBoundingRect().contains(event.scenePos()):
                self.moveBy(npos.x(), npos.y())
                self.drag1.moveBy(npos.x(), npos.y())
                self.drag2.moveBy(npos.x(), npos.y())
            self.drag_pos = event.scenePos()
            self.model.fixture_move_callback(self)

        event.ignore()
        #super(FixtureWidget, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.shape().contains(event.pos()):
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
        if self.shape().contains(event.pos()):
            if not self.dragging:
                if event.button() == QtCore.Qt.MouseButton.LeftButton and self.shape().contains(event.pos()):
                    self.select(not self.isSelected())
                    # TODO: Implement multi-select with control or shift key
                    multi = False
                    self.model._controller.widget_selected(self.isSelected(), self.model, multi)
                    self.canvas.on_fixture_click(self)

            if event.button() == QtCore.Qt.MouseButton.MiddleButton:
                if not self.about_to_delete:
                    self.about_to_delete = True
                else:
                    self.model.request_destruction()
            else:
                self.about_to_delete = False

            if event.button() == QtCore.Qt.MouseButton.RightButton and self.isSelected() and not self.model._controller.scene.get("locked", False):
                temp = self.drag1
                self.drag1 = self.drag2
                self.drag2 = temp
                self.update_handle_positions()

            self.dragging = False
            self.mouse_down = False
            self.drag_pos = None
            self.model.fixture_move_callback(self)
        else:
            if self.isSelected():
                self.select(not self.isSelected())
                self.model._controller.widget_selected(self.isSelected(), self.model, False)

    def mouseDoubleClickEvent(self, event):
        if self.shape().contains(event.pos()) and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.model.set_all(self.canvas.markup_color)

    def update_handle_positions(self):
        self.model.set_pos1([int(self.drag1.scene_x), int(self.drag1.scene_y)])
        x, y = self.canvas.scene_to_canvas(self.drag1.scene_x, self.drag1.scene_y)
        self.setPos(x, y)
        self.model.set_pos2([int(self.drag2.scene_x), int(self.drag2.scene_y)])
        self.update_geometry()

    def handle_move_callback(self, handle):
        self.update_handle_positions()
