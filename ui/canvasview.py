from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QFont, QPen
from PyQt5.QtQuick import QQuickPaintedItem

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
        self.model = self.controller.model

        self.setFillColor(QColor(0, 0, 0))
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setAcceptHoverEvents(False)

    def scene_to_canvas(self, coord):
        """
        Returns a scene coordinate tuple (x, y) transformed to canvas space
        """
        canvas_width, canvas_height = self.model.size
        scale_x = self.width() / canvas_width
        scale_y = self.height() / canvas_height
        scale = min(scale_x, scale_y)
        # TODO: add offets to center the view when aspect ratio is wrong
        return (coord[0] * scale, coord[1] * scale)

    def canvas_to_scene(self, coord):
        """
        Returns a canvas coordinate tuple (x, y) transformed to scene space
        """
        canvas_width, canvas_height = self.model.size
        scale_x = canvas_width / self.width()
        scale_y = canvas_height / self.height()
        scale = min(scale_x, scale_y)
        # TODO: add offets to center the view when aspect ratio is wrong
        return (coord[0] * scale, coord[1] * scale)

    def paint(self, painter):

        # Pixel data

        # Overlay UI
        for pg in self.model.pixel_groups:
            self.painters[pg.__class__](self, painter, pg)

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

        # Bounding box (debug)
        c = QColor(255, 0, 255, 50) if pg.selected else QColor(255, 255, 0, 50)
        painter.setPen(QPen(c, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(ax, ay, bx - ax, by - ay)

        # Pixel colors (maybe move to a separate render pass)
        colors = self.model.color_data.get(pg.address[0], None)
        if colors is not None:
            colors = colors[:,pg.address[1]:pg.address[1] + pg.count]
            #print(colors)

            painter.setPen(QColor(0, 0, 0, 0))
            for i, loc in enumerate(pg.pixel_locations):
                px, py = self.scene_to_canvas(loc)
                r, g, b = colors[i]
                painter.setBrush(QColor(r, g, b, 50))
                # TODO: probably want a better LED scaling than this.
                rx, ry = self.scene_to_canvas((8, 8))
                painter.drawEllipse(QPointF(px, py), rx, ry)

    painters = {
        LinearPixelGroup: _paint_linear_pixel_group
    }

    def hoverMoveEvent(self, event):
        self.controller.on_hover_move(event)

    def mouseMoveEvent(self, event):
        self.controller.on_mouse_move(event)

    def mousePressEvent(self, event):
        self.controller.on_mouse_press(event)

    def mouseReleaseEvent(self, event):
        self.controller.on_mouse_release(event)
