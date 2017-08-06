from PyQt5.QtCore import QObject, Qt, QPoint, QPointF, QRect, QRectF, QSizeF, \
                         QMargins, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics
from PyQt5.QtQuick import QQuickPaintedItem
from PyQt5.QtQml import QQmlListProperty

from controllers.canvascontroller import CanvasController
from models.pixelgroup import *


class CanvasView(QQuickPaintedItem):
    """
    CanvasView is responsible for drawing the simulation scene and the GUI
    chrome related to manipulating the scene.
    """

    def __init__(self, parent):
        super(CanvasView, self).__init__()
        self.parent = parent
        self.controller = CanvasController(self)
        self._model = self.controller.model

        self.setFillColor(QColor(0, 0, 0))
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setAcceptHoverEvents(True)
        self.forceActiveFocus()

        self.cursor_loc = None

    selection_changed = pyqtSignal()
    model_changed = pyqtSignal()

    @pyqtProperty(QObject, notify=model_changed)
    def model(self):
        return self._model

    @model.setter
    def model(self, val):
        self._model = val

    @pyqtProperty(QQmlListProperty, notify=selection_changed)
    def selection(self):
        return QQmlListProperty(PixelGroup, self, self.controller.selected)

    def geometryChanged(self, old_rect, new_rect):
        pass

    def scene_to_canvas(self, coord):
        """
        Returns a scene coordinate tuple (x, y) transformed to canvas space
        """
        canvas_width, canvas_height = self.model.size
        scale_x = self.width() / canvas_width
        scale_y = self.height() / canvas_height
        scale = min(scale_x, scale_y)
        # TODO: add offets to center the view when aspect ratio is wrong
        scaled = (coord[0] * scale, coord[1] * scale)
        return scaled

    def canvas_to_scene(self, coord):
        """
        Returns a canvas coordinate tuple (x, y) transformed to scene space
        """
        canvas_width, canvas_height = self.model.size
        scale_x = canvas_width / self.width()
        scale_y = canvas_height / self.height()
        scale = max(scale_x, scale_y)
        # TODO: add offets to center the view when aspect ratio is wrong
        scaled = (coord[0] * scale, coord[1] * scale)
        return scaled

    def paint(self, painter):

        painter.setRenderHint(QPainter.Antialiasing)

        selected = [pg for pg in self.model.pixel_groups if pg.selected]
        s = set(selected)
        unselected = [pg for pg in self.model.pixel_groups if pg not in s]

        for pg in unselected:
            self.painters[pg.__class__](self, painter, pg)

        for pg in selected:
            self.painters[pg.__class__](self, painter, pg)

        # Debug - cursor drawing
        # if self.cursor_loc is not None:
        #     x, y = self.cursor_loc.x(), self.cursor_loc.y()
        #     painter.setPen(QPen(QColor(255, 255, 0, 255),
        #                               1,
        #                               Qt.SolidLine,
        #                               Qt.RoundCap,
        #                               Qt.RoundJoin))
        #     painter.drawLine(QPointF(x - 5, y),QPointF(x + 5, y))
        #     painter.drawLine(QPointF(x, y - 5),QPointF(x, y + 5))

        # Stats
        # f = QFont()
        # f.setPointSize(8)
        # painter.setFont(f)
        # painter.setPen(QColor(170, 170, 200, 255))
        # painter.drawText(8, 16, "%0.1f packets/sec" % self.net_stats['pps'])
        # painter.drawText(8, 32, "%0.1f frames/sec" % self.net_stats['ups'])

    def _paint_linear_pixel_group(self, painter, pg):
        x1, y1 = self.scene_to_canvas(pg.start)
        x2, y2 = self.scene_to_canvas(pg.end)
        ax, ay = min(x1, x2), min(y1, y2)
        bx, by = max(x1, x2), max(y1, y2)

        # Pixel colors (maybe move to a separate render pass)
        colors = self.model.color_data.get(pg.strand, None)
        if colors is not None:
            painter.setCompositionMode(QPainter.CompositionMode_Lighten)
            colors = colors[pg.offset:pg.offset + pg.count]

            painter.setPen(QColor(0, 0, 0, 0))

            if self.model.blurred:
                spacing = 4
                for i, loc in enumerate(pg.pixel_locations[::spacing]):
                    px, py = self.scene_to_canvas(loc)
                    r, g, b = colors[i]
                    painter.setBrush(QColor(r, g, b, 50))
                    # TODO: probably want a better LED scaling than this.
                    rx, ry = self.scene_to_canvas((8, 8))

                    painter.setBrush(QColor(r, g, b, 50))
                    painter.drawEllipse(QPointF(px, py), 16, 16)

                spacing = 3
            else:
                spacing = 1

            for i, loc in enumerate(pg.pixel_locations[::spacing]):
                px, py = self.scene_to_canvas(loc)
                r, g, b = colors[i]
                painter.setBrush(QColor(r, g, b, 50))
                # TODO: probably want a better LED scaling than this.
                rx, ry = self.scene_to_canvas((8, 8))
                #painter.drawEllipse(QPointF(px, py), rx, ry)

                rx, ry = self.scene_to_canvas((3, 3))
                painter.setBrush(QColor(r, g, b, 255))
                painter.drawEllipse(QPointF(px, py), rx, ry)

            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        if self.model.design_mode:
            # Bounding box (debug)
            # c = QColor(255, 0, 255, 250) if pg.selected else QColor(255, 255, 0, 250)
            # if pg.selected:
            #     self._draw_bounding_box(painter, pg, c)

            if pg.selected or pg.hovering:
                painter.setPen(QPen(QColor(100, 100, 255, 170),
                                          8,
                                          Qt.SolidLine,
                                          Qt.RoundCap,
                                          Qt.RoundJoin))
                painter.drawLine(QPointF(x1, y1),QPointF(x2, y2))

            painter.setPen(QPen(QColor(100, 100, 100, 200),
                                      4,
                                      Qt.SolidLine,
                                      Qt.RoundCap,
                                      Qt.RoundJoin))
            painter.drawLine(QPointF(x1, y1),QPointF(x2, y2))

            if pg.selected:
                self._draw_drag_handle(painter, (x1, y1), False, False)
                self._draw_drag_handle(painter, (x2, y2), False, False)
                self._draw_address(painter, pg)

    painters = {
        LinearPixelGroup: _paint_linear_pixel_group
    }

    def _draw_bounding_box(self, painter, pg, color):
        x, y, w, h = pg.bounding_box()
        x, y = self.scene_to_canvas((x, y))
        w, h = self.scene_to_canvas((w, h))
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setPen(QPen(color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(x, y, w, h)

    def _draw_drag_handle(self, painter, location, hovering, dragging):
        x, y = location
        painter.setPen(QPen(QColor(200, 200, 200, 200), 1, Qt.SolidLine))
        if hovering:
            painter.setBrush(QColor(50, 100, 255, 255))
            rect = QRectF(x - 6, y - 6, 12, 12)
            painter.drawRoundedRect(rect, 1, 1)
        painter.setBrush(QColor(0, 0, 0, 0))
        rect = QRectF(x - 4, y - 4, 8, 8)
        painter.drawRoundedRect(rect, 1, 1)

    def _draw_address(self, painter, pg):
        x1, y1 = self.scene_to_canvas(pg.start)
        x2, y2 = self.scene_to_canvas(pg.end)
        label_pos = QPoint((x1 + x2) / 2, (y1 + y2) / 2)

        label_font = QFont()
        label_font.setPointSize(8)
        painter.setFont(label_font)

        label_string = "%d:%d" % (pg.strand, pg.offset)
        fm = QFontMetrics(label_font)
        text_rect = fm.boundingRect(label_string)
        text_rect += QMargins(5, 2, 5, 2)
        label_rect = QRect(label_pos - QPoint(12, 7), text_rect.size())

        painter.setBrush(QColor(128, 64, 128, 220))
        painter.setPen(QColor(100, 100, 100, 100))
        painter.drawRoundedRect(label_rect, 5, 5)
        painter.setPen(QColor(255, 255, 255, 255))
        painter.drawText(label_rect, Qt.AlignCenter, label_string)

    def hoverMoveEvent(self, event):
        self.controller.on_hover_move(event)

    def mouseMoveEvent(self, event):
        self.controller.on_mouse_move(event)

    def mousePressEvent(self, event):
        self.controller.on_mouse_press(event)

    def mouseReleaseEvent(self, event):
        self.controller.on_mouse_release(event)

    def keyPressEvent(self, event):
        event.accept()
        self.controller.on_key_press(event)

    def keyReleaseEvent(self, event):
        event.accept()
        self.controller.on_key_release(event)
