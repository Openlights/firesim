import array
import time

from PyQt5.QtCore import (QObject, Qt, QPoint, QPointF, QRect, QRectF, QSizeF,
                          QMargins, pyqtSignal, pyqtSlot, pyqtProperty)
from PyQt5.QtGui import (QPainter, QColor, QFont, QPen, QFontMetrics,
                         QOpenGLVersionProfile, QSurfaceFormat,
                         QOpenGLShader, QOpenGLShaderProgram)
from PyQt5.QtQuick import QQuickPaintedItem
from PyQt5.QtQml import QQmlListProperty

from controllers.canvascontroller import CanvasController
from models.pixelgroup import *


class CanvasView(QQuickPaintedItem):
    """
    CanvasView is responsible for drawing the simulation scene and the GUI
    chrome related to manipulating the scene.
    """

    ENABLE_OPENGL = False

    def __init__(self, parent):
        super(CanvasView, self).__init__()
        self.parent = parent
        self.controller = CanvasController(self)
        self._model = self.controller.model

        self.setRenderTarget(QQuickPaintedItem.FramebufferObject)
        self.setFillColor(QColor(0, 0, 0, 255))
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setAcceptHoverEvents(True)
        self.forceActiveFocus()

        #self.renderer = CanvasRenderer()

        self.cursor_loc = None

        self.gl = None

        self._last_render_times = []
        self._fps = 0

        self.windowChanged.connect(self.on_window_changed)

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

    def on_window_changed(self, window):
        self.init_opengl()

    def init_opengl(self):
        ctx = self.window().openglContext()
        if ctx is not None:
            self.gl = ctx.versionFunctions(
                          QOpenGLVersionProfile(QSurfaceFormat()))
            self.gl.initializeOpenGLFunctions()
        else:
            print("No opengl context")
            return

        pixel_shader_src = '''
void main() {
    vec2 pos = mod(gl_FragCoord.xy, vec2(50.0)) - vec2(25.0);
    float dist_squared = dot(pos, pos);

    gl_FragColor = mix(vec4(.90, .90, .90, 1.0), vec4(.20, .20, .40, 1.0),
                       smoothstep(380.25, 420.25, dist_squared));
}
 '''

        self.program = QOpenGLShaderProgram(self)

        self.program.addShaderFromSourceCode(QOpenGLShader.Fragment,
                pixel_shader_src)

        self.program.link()

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

        start = time.time()

        if self.ENABLE_OPENGL:
            if self.gl is not None:
                painter.beginNativePainting()

                gl = self.gl

                gl.glEnable(gl.GL_SCISSOR_TEST);
                gl.glScissor(0, 0, self.width(), self.height());

                gl.glClearColor(1.0, 0.0, 1.0, 1.0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)

                self.program.bind()

                vertices = array.array("f", [
                    0, 0,
                    400, 400,
                    800, 800,
                    200, 200
                ])

                indices = array.array("B", [0,1,2,0,2,3])

                #gl.glEnableVertexAttribArray(self.vAttr)

                # gl.glVertexAttribPointer(self.vAttr,
                #     2,
                #     gl.GL_FLOAT,
                #     gl.GL_FALSE,
                #     0,
                #     vertices)

                #gl.glDrawArrays(gl.GL_TRIANGLES, 0, 4)
                gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_BYTE, indices)

                #gl.glDisableVertexAttribArray(self.vAttr)

                self.program.release()

                gl.glDisable(gl.GL_SCISSOR_TEST);

                painter.endNativePainting()
            else:
                if self.window().openglContext() is not None:
                    # TODO: Re-init OpenGL but on the right thread
                    self.init_opengl()

        painter.setRenderHint(QPainter.Antialiasing)

        selected = [pg for pg in self.model.pixel_groups if pg.selected]
        s = set(selected)
        unselected = [pg for pg in self.model.pixel_groups if pg not in s]

        for pg in unselected:
            self.painters[pg.__class__](self, painter, pg)

        for pg in selected:
            self.painters[pg.__class__](self, painter, pg)

        self._render_pixels_this_frame = False

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

        frame_time = 1.0 / (time.time() - start)

        if len(self._last_render_times) < 5:
            self._last_render_times.append(frame_time)
        else:
            self._fps = sum(self._last_render_times) / 5
            self._last_render_times.clear()

        # Stats
        f = QFont()
        f.setPointSize(8)
        painter.setFont(f)
        painter.setPen(QColor(170, 170, 200, 255))
        #painter.drawText(8, 16, "%0.1f packets/sec" % self.net_stats['pps'])
        painter.drawText(8, 32, "%d fps" % self._fps)

    def _paint_linear_pixel_group(self, painter, pg):
        x1, y1 = self.scene_to_canvas(pg.start)
        x2, y2 = self.scene_to_canvas(pg.end)

        if self.controller.dragging and pg.selected:
            dx = self.controller.drag_delta.x()
            dy = self.controller.drag_delta.y()
        else:
            dx = 0
            dy = 0

        x1 += dx
        x2 += dx
        y1 += dy
        y2 += dy

        ax, ay = min(x1, x2), min(y1, y2)
        bx, by = max(x1, x2), max(y1, y2)

        # Pixel colors (maybe move to a separate render pass)
        colors = self.model.color_data.get(pg.strand, None)
        if colors is not None:

            colors = colors[pg.offset:pg.offset + pg.count]

            painter.setPen(QColor(0, 0, 0, 0))

            if self.model.blurred:
                spacing = 4
                for i, loc in enumerate(pg.pixel_locations[::spacing]):
                    px, py = self.scene_to_canvas(loc)
                    px += dx
                    py += dy
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
                px += dx
                py += dy
                r, g, b = colors[i]
                painter.setBrush(QColor(r, g, b, 50))
                # TODO: probably want a better LED scaling than this.
                rx, ry = self.scene_to_canvas((8, 8))
                #painter.drawEllipse(QPointF(px, py), rx, ry)

                rx, ry = self.scene_to_canvas((3, 3))
                painter.setBrush(QColor(r, g, b, 255))
                painter.drawEllipse(QPointF(px, py), rx, ry)

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
                self._draw_address(painter, pg, (dx, dy))

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

    def _draw_address(self, painter, pg, offset):
        x1, y1 = self.scene_to_canvas(pg.start)
        x2, y2 = self.scene_to_canvas(pg.end)
        label_pos = QPoint((x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1])

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


class CanvasRenderer(QObject):

    def __init__(self):
        super(QObject, self).__init__()

    @pyqtSlot()
    def paint(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
