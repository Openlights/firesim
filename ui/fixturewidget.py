from __future__ import division
from past.utils import old_div
import logging as log

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QPointF, QSizeF
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF, QFont
from PyQt5.QtQuick import QQuickItem, QQuickPaintedItem

from ui.draghandlewidget import DragHandleWidget


class FixtureWidget(QQuickPaintedItem):

    # Margin, in pixels, of the drawing rectangle
    SHAPE_MARGIN = 16

    def __init__(self, canvas, model):
        super(FixtureWidget, self).__init__(canvas)
        #self.setFlag(QQuickItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton |
                                     QtCore.Qt.MiddleButton |
                                     QtCore.Qt.RightButton)
        self.setAcceptHoverEvents(True)
        self.setFillColor(QColor(0, 0, 0, 0))

        self.model = model
        self.about_to_delete = False
        self.setHeight(16)
        self.setWidth(128)
        self.dragging = False
        self.mouse_down = False
        self.selected = False
        self.hovering = False
        self.drag_pos = None
        self.origin = None
        self._shape = None

        self.canvas = canvas
        self.setParent(canvas)

        if self.model.pos1() == (-1, -1):

            x, y = canvas.get_next_new_fixture_pos_and_increment()

            x, y = (int(self.x()), int(self.y()))

            self.model.set_pos1(self.canvas.canvas_to_scene(x, y))
            self.model.set_pos2(self.canvas.canvas_to_scene(x + 100, y + 100))

        x1, y1 = canvas.scene_to_canvas(self.model.pos1())
        x2, y2 = canvas.scene_to_canvas(self.model.pos2())
        self.setPos(min(x1, x2), min(y1, y2))
        self.update_geometry()

        self.drag1 = DragHandleWidget(canvas=canvas, fixture=self, pos=self.model.pos1())
        self.drag2 = DragHandleWidget(canvas=canvas, fixture=self, pos=self.model.pos2())

    def setPos(self, x, y):
        self.setX(x - self.SHAPE_MARGIN)
        self.setY(y - self.SHAPE_MARGIN)

    def deleteLater(self):
        self.drag1.deleteLater()
        self.drag2.deleteLater()
        super(FixtureWidget, self).deleteLater()

    def update_geometry(self):
        """
        The width and height properties determine the paintable area,
        so they need to include margin for the fixture border and selection hover graphics.
        """
        p1 = self.canvas.scene_to_canvas(self.model.pos1())
        p2 = self.canvas.scene_to_canvas(self.model.pos2())
        self.setWidth(abs(p2[0] - p1[0]) + (4 * self.SHAPE_MARGIN))
        self.setHeight(abs(p2[1] - p1[1]) + (4 * self.SHAPE_MARGIN))
        self.update()

    def shape(self):
        """Defines a 4-gon for mouse selection/hovering, larger than the drawn fixture"""
        if self._shape is None:
            x1, y1 = self.model.pos1()
            x2, y2 = self.model.pos2()

            p1 = QPointF(x1 - self.x() + self.SHAPE_MARGIN, y1 - self.y() + self.SHAPE_MARGIN)
            p2 = QPointF(x2 - self.x() + self.SHAPE_MARGIN, y2 - self.y() + self.SHAPE_MARGIN)

            path = QPainterPath()
            line = QtCore.QLineF(p1, p2)
            offset1 = line.normalVector().unitVector()

            if self.selected:
                offset1.setLength(11)
            else:
                offset1.setLength(9)

            ol1 = QtCore.QLineF(p1, p2)
            ol1.translate(offset1.dx(), offset1.dy())
            ol2 = QtCore.QLineF(p1, p2)
            ol2.translate(-offset1.dx(), -offset1.dy())

            p = QPolygonF([
                QtCore.QPoint(ol1.x1(), ol1.y1()),
                QtCore.QPoint(ol1.x2(), ol1.y2()),
                QtCore.QPoint(ol2.x2(), ol2.y2()),
                QtCore.QPoint(ol2.x1(), ol2.y1())
            ])

            path.addPolygon(p)
            path.closeSubpath()
            self._shape = path

        return self._shape

    def paint(self, painter):
        # if self.selected:
        #     painter.setPen(QPen(QColor(255, 0, 255, 225),
        #                           1,
        #                           QtCore.Qt.SolidLine,
        #                           QtCore.Qt.RoundCap,
        #                           QtCore.Qt.RoundJoin))
        #     painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        x1, y1 = self.model.pos1()
        x2, y2 = self.model.pos2()

        p1 = QPointF(x1 - self.x() + self.SHAPE_MARGIN, y1 - self.y() + self.SHAPE_MARGIN)
        p2 = QPointF(x2 - self.x() + self.SHAPE_MARGIN, y2 - self.y() + self.SHAPE_MARGIN)

        if self.hovering:
            painter.setPen(QPen(QColor(200, 200, 255, 100),
                                      12,
                                      QtCore.Qt.SolidLine,
                                      QtCore.Qt.RoundCap,
                                      QtCore.Qt.RoundJoin))
            painter.drawLine(p1, p2)

        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(127, 127, 127, 20),
                                  6,
                                  QtCore.Qt.SolidLine,
                                  QtCore.Qt.RoundCap,
                                  QtCore.Qt.RoundJoin))
        painter.drawLine(p1, p2)
        if self.selected:
            if self.about_to_delete:
                painter.setPen(QPen(QColor(255, 50, 50, 225),
                                          10,
                                          QtCore.Qt.SolidLine,
                                          QtCore.Qt.RoundCap,
                                          QtCore.Qt.RoundJoin))
            else:
                painter.setPen(QPen(QColor(50, 100, 255, 225),
                                          10,
                                          QtCore.Qt.SolidLine,
                                          QtCore.Qt.RoundCap,
                                          QtCore.Qt.RoundJoin))
            painter.drawLine(p1, p2)

        painter.setCompositionMode(QPainter.CompositionMode_Lighten)

        if self.model.pixels() > 0:
            data = self.model.pixel_data()
            color_line = QtCore.QLineF(p1, p2)
            color_line.setLength(old_div(color_line.length(), self.model.pixels()))
            painter.setPen(QPen(QColor(0, 0, 0, 0), 0))

            if self.canvas.gui.state.blur_enable:
                spacing = 4
                for pixel in data[::spacing]:
                    px, py = color_line.x1(), color_line.y1()
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    painter.setBrush(QColor(r, g, b, 50))
                    #painter.setPen(QPen(QColor(r, g, b, 60),
                    #                          5,
                    #                          QtCore.Qt.SolidLine))
                    painter.drawEllipse(QtCore.QPointF(px, py), 16, 16)
                    #painter.drawLine(color_line.unitVector())
                    color_line.translate(color_line.dx()*spacing, color_line.dy()*spacing)

                color_line = QtCore.QLineF(p1, p2)
                color_line.setLength(old_div(color_line.length(), self.model.pixels()))
                painter.setPen(QPen(QColor(0, 0, 0, 0), 0))
                spacing = 3
            else:
                spacing = 1

            for pixel in data[::spacing]:
                px, py = color_line.x1(), color_line.y1()
                r, g, b = pixel[0], pixel[1], pixel[2]
                painter.setBrush(QColor(r, g, b, 255))
                #painter.setPen(QPen(QColor(r, g, b, 60),
                #                          5,200
                #                          QtCore.Qt.SolidLine))
                painter.drawEllipse(QtCore.QPointF(px, py), 3, 3)
                painter.setBrush(QColor(r, g, b, 50))
                painter.drawEllipse(QtCore.QPointF(px, py), 6, 6)
                #painter.drawLine(color_line.unitVector())
                color_line.translate(color_line.dx()*spacing, color_line.dy()*spacing)

        if self.hovering or self.selected or self.canvas.gui.state.labels_visible:
            label_pos = (p1 + p2) / 2
            label_font = QFont()
            label_font.setPointSize(8)
            painter.setFont(label_font)
            label_rect = QtCore.QRectF(label_pos - QPointF(12, 7), QSizeF(24, 14))
            painter.setBrush(QColor(128, 64, 128, 220))
            painter.setPen(QColor(100, 100, 100, 100))
            painter.drawRoundedRect(label_rect, 5, 5)
            painter.setPen(QColor(255, 255, 255, 255))
            painter.drawText(label_rect, QtCore.Qt.AlignCenter, "%d:%d" % (self.model.strand(), self.model.address()))

        #painter.fillRect(self.boundingRect(), QColor(255, 255, 0, 255))

    def hover_enter(self):
        if self.canvas.gui.state.locked:
            return

        self.hovering = True
        self.setZ(100)
        self.drag1.setZ(101)
        self.drag2.setZ(101)
        self.drag1.hovering = True
        self.drag2.hovering = True
        self.drag1.hidden = False
        self.drag2.hidden = False
        #else:
        #    self.hovering = False
        #    self.drag1.hovering = False
        #    self.drag2.hovering = False
        #    self.drag1.hidden = not self.selected
        #    self.drag2.hidden = not self.selected

        self.drag1.update()
        self.drag2.update()
        self.update()

    def hover_leave(self):
        if self.canvas.gui.state.locked:
            return

        self.setZ(0)
        self.hovering = False
        self.drag1.hovering = False
        self.drag2.hovering = False
        self.drag1.hidden = not self.selected
        self.drag2.hidden = not self.selected
        self.drag1.update()
        self.drag2.update()

    def hoverEnterEvent(self, event):
        event.accept()

    def hoverLeaveEvent(self, event):
        event.ignore()

    def hoverMoveEvent(self, event):
        if self.canvas.gui.state.locked:
            event.ignore()
            return

        if self.check_hover(event.pos()):
            event.accept()

    def check_hover(self, pos):
        if self.shape().contains(pos):
            self.setZ(50)
            self.drag1.setZ(60)
            self.drag2.setZ(60)
            self.hovering = True
            self.drag1.hidden = False
            self.drag2.hidden = False
        else:
            self.hovering = False
            if not self.selected:
                self.setZ(0)
                self.drag1.setZ(0)
                self.drag2.setZ(0)
            self.drag1.hidden = not self.selected
            self.drag2.hidden = not self.selected

        self.drag1.update()
        self.drag2.update()
        self.update()
        return self.hovering

    def mouseMoveEvent(self, event):

        DRAG_THRESHOLD = 4  # pixels

        if self.selected and self.mouse_down and not self.canvas.gui.state.locked:
            event.accept()

            delta_pos = event.globalPos() - self.drag_pos

            if self.dragging or max(delta_pos) > DRAG_THRESHOLD:
                self.dragging = True

                if self.canvas.contains(self.canvas.mapFromGlobal(event.globalPos())):
                    self.moveBy(npos.x(), npos.y())
                    self.drag1.move_by(npos.x(), npos.y())
                    self.drag2.move_by(npos.x(), npos.y())
                    self.update_handle_positions()

                self.model.fixture_move_callback(self)
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if self.canvas.gui.state.locked:
            return

        if self.shape().contains(event.pos()):
            event.accept()
            self.mouse_down = True
            self.drag_pos = event.globalPos()
        else:
            event.ignore()

    def select(self, selected, multi=False):
        # if selected:
        #     print("Selected: ", repr(self.model), "X", self.x(), "Y", self.y(),
        #           "Width", self.width(), "Height", self.height())
        self.drag1.selected = selected
        self.drag2.selected = selected
        self.selected = selected
        if selected:
            self.setZ(100)
            self.drag1.setZ(150)
            self.drag2.setZ(150)
            self.drag1.hidden = False
            self.drag2.hidden = False
        else:
            self.setZ(0)
            self.drag1.setZ(0)
            self.drag2.setZ(0)
            self.drag1.hidden = True
            self.drag2.hidden = True
            self.hovering = False
        self.drag1.update()
        self.drag2.update()

    def mouseReleaseEvent(self, event):
        if self.shape().contains(event.pos()) and not self.canvas.gui.state.locked:
            if not self.dragging:
                if (event.button() == QtCore.Qt.LeftButton
                    and self.shape().contains(event.pos())):
                    self.select(not self.selected)
                    # TODO: Implement multi-select with control or shift key
                    multi = False
                    self.model._controller.widget_selected(self.selected, self.model, multi)
                    self.canvas.on_fixture_click(self)

            if event.button() == QtCore.Qt.MiddleButton:
                if not self.about_to_delete:
                    self.about_to_delete = True
                else:
                    self.model.request_destruction()
            else:
                self.about_to_delete = False

            if (event.button() == QtCore.Qt.RightButton
                and self.selected and not self.canvas.gui.state.locked):
                temp = self.drag1
                self.drag1 = self.drag2
                self.drag2 = temp
                self.update_handle_positions()
                self.drag1.update()
                self.drag2.update()

            self.dragging = False
            self.mouse_down = False
            self.drag_pos = None
            self.model.fixture_move_callback(self)
        else:
            if not self.dragging:
                self.select(False)
            else:
                self.dragging = False

    def mouseDoubleClickEvent(self, event):
        pass

    def update_handle_positions(self):
        x, y = self.drag1.scene_x, self.drag1.scene_y
        self.model.set_pos1([int(x), int(y)])

        cx, cy = self.canvas.scene_to_canvas(x, y)
        #self.setPos(cx, cy)

        x, y = self.drag2.scene_x, self.drag2.scene_y
        self.model.set_pos2([int(x), int(y)])
        self.update_geometry()

    def handle_move_callback(self, handle):
        self.update_handle_positions()
